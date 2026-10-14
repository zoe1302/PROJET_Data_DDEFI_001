"""Test 2, la coupe figée : la même graine donne toujours les mêmes plis.

Les empreintes attendues sont écrites ici en dur : si elles changent, quelqu'un a touché à la
coupe, et il doit le dire dans DECISIONS.md avant de mettre ce test à jour.
"""

from credit.split import FOLDS, fold_hash, make_split

EXPECTED = {
    "train": "adcf3e2a328c754645843c293b8f763edb848a3fc3b45fa91d29c81cef8fc0d9",
    "validation": "8e7ab5fc23e3b391497f5857f7d237f2a17233805a5cff90d1edf7d86e5424c7",
    "test": "38efbefd21811eea54be985d4beba3276310ce7f80b39bbb0679689c494fdbd6",
}


def test_split_is_frozen(raw, cfg):
    folds = make_split(raw, cfg)
    sizes = {k: len(v) for k, v in folds.items()}
    assert sizes == {"train": 18_000, "validation": 6_000, "test": 6_000}
    ids = set()
    for name in FOLDS:
        new = set(folds[name]["ID"])
        assert not (ids & new), "un client dans deux plis : fuite"
        ids |= new
    for name in FOLDS:
        assert fold_hash(folds[name]) == EXPECTED[name], f"la coupe « {name} » a changé"
