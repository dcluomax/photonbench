import pytest

from photonbench.claims import Capability, require_claim, require_nonclassical_witness


def test_processed_frame_cannot_claim_photons() -> None:
    with pytest.raises(ValueError):
        require_claim(Capability.PROCESSED_FRAME, "photon-counting-statistics")


def test_nonclassical_claim_requires_confidence_bound_below_one() -> None:
    require_nonclassical_witness(
        witness="g2-antibunching",
        estimate=0.4,
        upper_confidence_bound=0.7,
    )
    with pytest.raises(ValueError):
        require_nonclassical_witness(
            witness="g2-antibunching",
            estimate=0.8,
            upper_confidence_bound=1.1,
        )

