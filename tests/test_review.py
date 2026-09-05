import pytest

from rachel_loop_engine.review import MediaReview, parse_media_review, recommend_variant, render_review_card


def test_parse_review_contract():
    text = 'RLE_REVIEW_JSON\n{"passed":true,"overall_score":93,"story_truthfulness":5,"hook_strength":4.2,"pacing":4.5,"caption_quality":4,"audio_quality":4.5,"loop_seam":null,"warnings":[],"notes":["good"]}'
    r = parse_media_review(text, "natural")
    assert r.overall_score == 93
    assert r.notes == ["good"]


def test_missing_marker_fails_closed():
    with pytest.raises(ValueError):
        parse_media_review('{"passed": true}', "natural")


def test_recommendation_uses_passing_high_score_and_conservative_tie_break():
    a = MediaReview("natural", True, 90, 5, 4, 4)
    b = MediaReview("retention", True, 94, 5, 4.5, 4.5)
    c = MediaReview("loop", False, 99, 5, 5, 5, loop_seam=2)
    assert recommend_variant([a, b, c]) == "retention"
    card = render_review_card([a, b, c])
    assert "**Recommended:** retention" in card


def test_review_roundtrip_dict():
    from rachel_loop_engine.review import review_from_dict, review_to_dict
    r = MediaReview("loop", True, 91, 5, 4.5, 4.2, loop_seam=4.7)
    assert review_from_dict(review_to_dict(r)) == r
