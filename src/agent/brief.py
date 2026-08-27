"""
Urban Heat Brief composition.

This module turns already-normalized application evidence into a concise,
attributable brief. It does not call providers and it does not add data to
the decision model. Every factual sentence retains its source, mode, time,
and evidence-node references.
"""

from datetime import datetime, timezone


TIE_THRESHOLD_CELSIUS = 0.1


def _number(value, digits=2):
    """Format a numeric evidence value without inventing a value."""
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def _coordinate(coordinate):
    """Format a [longitude, latitude] coordinate for human reading."""
    if not coordinate or len(coordinate) < 2:
        return "the selected location"
    return f"{coordinate[1]:.4f}°N, {abs(coordinate[0]):.4f}°W"


def _claim(
    claim_id,
    text,
    source_provider,
    source_type,
    evidence_nodes,
    mode,
    observation_time=None,
    retrieved_at=None,
    effective_period=None,
    used_in_decision=False,
    governing_threshold=None,
):
    """Create the machine-readable claim envelope used by the Brief."""
    return {
        "claim_id": claim_id,
        "text": text,
        "source_provider": source_provider,
        "source_type": source_type,
        "evidence_nodes": evidence_nodes,
        "mode": mode,
        "observation_time": observation_time,
        "retrieved_at": retrieved_at,
        "effective_period": effective_period,
        "used_in_decision": used_in_decision,
        "governing_threshold_celsius": governing_threshold,
    }


def _section(section_id, heading, claims):
    return {
        "section_id": section_id,
        "heading": heading,
        "claims": claims,
        "text": " ".join(claim["text"] for claim in claims),
    }


def _nws_section(mode, nws_context, observation_time):
    """Compose NWS context without turning it into thermal evidence."""
    if mode == "replay":
        text = "Current NWS context is not included in historical Replay."
        return _section(
            "weather_context",
            "Weather context",
            [
                _claim(
                    "weather-replay-exclusion",
                    text,
                    "UHI",
                    "provenance_disclosure",
                    ["nws_exclusion"],
                    "replay",
                    observation_time=observation_time,
                    used_in_decision=False,
                )
            ],
        )

    nws = nws_context or {}
    retrieved_at = nws.get("retrieved_at")
    conditions = nws.get("conditions") or {}
    alerts = nws.get("alerts") or []
    effective_period = {
        "start": conditions.get("effective_start"),
        "end": conditions.get("effective_end"),
    }
    if not any(effective_period.values()):
        effective_period = None

    if not conditions and not alerts:
        text = "NWS context was unavailable for this LIVE query; it is not used in the thermal decision."
        return _section(
            "weather_context",
            "Weather context",
            [
                _claim(
                    "weather-live-unavailable",
                    text,
                    "NWS",
                    "availability_disclosure",
                    ["nws_request", "nws_result"],
                    "live",
                    observation_time=observation_time,
                    retrieved_at=retrieved_at,
                    used_in_decision=False,
                )
            ],
        )

    sentences = []
    if conditions:
        forecast = conditions.get("short_forecast")
        if forecast:
            sentences.append(f"The National Weather Service reports {forecast} conditions for Phoenix.")
    if alerts:
        # Keep the summary conservative and avoid repeating duplicate alerts.
        events = []
        for alert in alerts:
            event = alert.get("event")
            if event and event not in events:
                events.append(event)
        if events:
            joined = ", ".join(events[:3])
            sentences.append(f"NWS lists active alerts including {joined}.")
    if not sentences:
        sentences.append("NWS current context was retrieved for Phoenix.")

    claims = [
        _claim(
            f"weather-live-{index + 1}",
            sentence,
            "NWS",
            "official_current_context",
            ["nws_result"],
            "live",
            observation_time=observation_time,
            retrieved_at=retrieved_at,
            effective_period=effective_period,
            used_in_decision=False,
        )
        for index, sentence in enumerate(sentences)
    ]
    return _section("weather_context", "Weather context", claims)


def compose_urban_heat_brief(result, nws_context=None):
    """
    Compose a first-class Urban Heat Brief from an existing agent result.

    Returns None when FortyGuard did not produce a usable heatmap. Optional
    sources enrich the Brief but never determine the thermal ranking.
    """
    answer = result.get("answer", {})
    if answer.get("error"):
        return None

    mode = answer.get("mode")
    if mode not in ("live", "replay"):
        return None

    conditions = answer.get("conditions", {})
    raw_heatmap = result.get("raw_results", {}).get("heatmap") or {}
    heatmap_result = raw_heatmap.get("result", {})
    feature_count = heatmap_result.get("feature_count") or conditions.get("feature_count") or 0
    if not raw_heatmap or not feature_count:
        return None

    observation_time = raw_heatmap.get("observation_time") or answer.get("observation_time")
    ranked = conditions.get("ranked_candidates", [])
    leading = ranked[0] if ranked else None
    mean_temp = heatmap_result.get("mean_temperature_celsius")
    if mean_temp is None:
        mean_temp = conditions.get("area_mean_temperature_celsius")

    claims = []
    thermal_claims = []
    feature_text = (
        f"FortyGuard identified the highest measured thermal burden among "
        f"{feature_count} evaluated heatmap features."
    )
    thermal_claims.append(
        _claim(
            "thermal-feature-count",
            feature_text,
            "FortyGuard",
            "thermal_measurement",
            ["heatmap_result"],
            mode,
            observation_time=observation_time,
            used_in_decision=True,
        )
    )

    if leading:
        observed = leading.get("observed_temp")
        location_text = _coordinate(leading.get("coordinate"))
        measured_text = (
            f"The leading candidate near {location_text} measured approximately "
            f"{_number(observed)}°C against an area mean of {_number(mean_temp)}°C."
        )
        thermal_claims.append(
            _claim(
                "thermal-leading-candidate",
                measured_text,
                "FortyGuard",
                "thermal_measurement",
                ["heatmap_result", "coordinate_selection"],
                mode,
                observation_time=observation_time,
                used_in_decision=True,
            )
        )
        apparent = leading.get("apparent_temp")
        if apparent is not None:
            apparent_text = (
                f"FortyGuard environmental parameters at that candidate report an apparent "
                f"temperature of {_number(apparent)}°C."
            )
            thermal_claims.append(
                _claim(
                    "thermal-apparent-temperature",
                    apparent_text,
                    "FortyGuard",
                    "environmental_measurement",
                    ["env_params_result"],
                    mode,
                    observation_time=leading.get("observation_time") or observation_time,
                    used_in_decision=True,
                )
            )

    claims.extend(thermal_claims)

    ranking_status = conditions.get("ranking_status")
    ranking_explanation = conditions.get("ranking_explanation")
    candidate_claims = []
    if ranked and ranking_status == "near_tie":
        candidate_count_text = {1: "One", 2: "Two", 3: "Three"}.get(len(ranked), str(len(ranked)))
        candidate_text = (
            f"{candidate_count_text} candidate locations show effectively equivalent thermal burden "
            f"in this observation. Their measured temperatures fall within the "
            f"{TIE_THRESHOLD_CELSIUS:.1f}°C near-tie tolerance, so thermal evidence alone "
            "does not support a meaningful distinction among them."
        )
        candidate_claims.append(
            _claim(
                "candidate-near-tie",
                candidate_text,
                "UHI",
                "product_derived_comparison",
                ["heatmap_result", "coordinate_selection"],
                mode,
                observation_time=observation_time,
                used_in_decision=True,
                governing_threshold=TIE_THRESHOLD_CELSIUS,
            )
        )
        if ranking_explanation:
            additional_text = "Additional local context would be needed before selecting one intervention location over another."
            candidate_claims.append(
                _claim(
                    "candidate-near-tie-context",
                    additional_text,
                    "UHI",
                    "product_derived_comparison",
                    ["heatmap_result", "coordinate_selection"],
                    mode,
                    observation_time=observation_time,
                    used_in_decision=True,
                    governing_threshold=TIE_THRESHOLD_CELSIUS,
                )
            )
    elif ranked:
        second = ranked[1] if len(ranked) > 1 else None
        third = ranked[2] if len(ranked) > 2 else None
        comparisons = []
        if second:
            comparisons.append(f"{leading.get('observed_temp', 0) - second.get('observed_temp', 0):.2f}°C above candidate #2")
        if third:
            comparisons.append(f"{leading.get('observed_temp', 0) - third.get('observed_temp', 0):.2f}°C above candidate #3")
        comparison_text = " and ".join(comparisons) if comparisons else "the highest observed temperature"
        clear_text = (
            f"Candidate #1 warrants first investigation on measured thermal burden: it was "
            f"{comparison_text}. This is a prioritization for investigation, not a claim of intervention effectiveness."
        )
        candidate_claims.append(
            _claim(
                "candidate-clear-ranking",
                clear_text,
                "UHI",
                "product_derived_comparison",
                ["heatmap_result", "coordinate_selection", "env_params_result"],
                mode,
                observation_time=observation_time,
                used_in_decision=True,
            )
        )
    else:
        candidate_claims.append(
            _claim(
                "candidate-comparison-not-requested",
                "This response summarizes the queried thermal field; no candidate comparison was requested.",
                "UHI",
                "product_derived_disclosure",
                ["plan", "heatmap_result"],
                mode,
                observation_time=observation_time,
                used_in_decision=True,
            )
        )
    claims.extend(candidate_claims)

    weather_section = _nws_section(mode, nws_context, observation_time)
    claims.extend(weather_section["claims"])

    if ranking_status == "near_tie":
        decision_text = "These locations warrant comparable attention on thermal evidence alone."
    elif ranked:
        decision_text = "Candidate #1 is the first location to investigate on measured thermal burden."
    else:
        decision_text = "The measured thermal field should guide where to investigate further."
    decision_claim = _claim(
        "decision-note",
        decision_text,
        "UHI",
        "product_derived_decision_note",
        ["plan", "heatmap_result", "coordinate_selection", "env_params_result"],
        mode,
        observation_time=observation_time,
        used_in_decision=True,
        governing_threshold=TIE_THRESHOLD_CELSIUS if ranking_status == "near_tie" else None,
    )
    claims.append(decision_claim)

    sections = [
        _section("thermal_finding", "Thermal finding", thermal_claims),
        _section("candidate_interpretation", "Candidate interpretation", candidate_claims),
        weather_section,
        _section("decision_note", "Decision note", [decision_claim]),
    ]

    source_list = [
        {
            "provider": "FortyGuard",
            "mode": mode,
            "source_type": "primary_thermal_measurement",
            "observation_time": observation_time,
            "endpoints": ["/v1/heatmap", "/v1/env_params"],
            "used_in_decision": True,
        }
    ]
    if mode == "live" and nws_context and (nws_context.get("conditions") or nws_context.get("alerts")):
        conditions = nws_context.get("conditions") or {}
        source_list.append(
            {
                "provider": "NWS",
                "mode": "live",
                "source_type": "official_current_context",
                "retrieved_at": nws_context.get("retrieved_at"),
                "effective_period": {
                    "start": conditions.get("effective_start"),
                    "end": conditions.get("effective_end"),
                },
                "endpoints": nws_context.get("source_endpoints", []),
                "used_in_decision": False,
            }
        )

    title = "Urban Heat Brief"
    mode_label = "Historical Replay" if mode == "replay" else "Live API"
    plain_lines = [f"{title} — {mode_label} — {observation_time or 'observation time unavailable'}"]
    for section in sections:
        plain_lines.append(f"\n{section['heading'].upper()}\n{section['text']}")
    plain_lines.append("\nSOURCES\n" + " · ".join(source["provider"] for source in source_list))
    plain_text = "".join(plain_lines)

    return {
        "title": title,
        "mode": mode,
        "mode_label": mode_label,
        "observation_time": observation_time,
        "sections": sections,
        "claims": claims,
        "sources": source_list,
        "ranking_status": ranking_status,
        "tie_threshold_celsius": TIE_THRESHOLD_CELSIUS,
        "plain_text": plain_text,
        "markdown": plain_text,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nws_used_in_decision": False,
    }
