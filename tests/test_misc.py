from your.utils.misc import *


def test_pad_along_axis():
    d = np.random.random((10, 10))
    d_end = pad_along_axis(d, 12, "end", 0, mode="median")
    assert d_end.shape[0] == 12
    assert (d_end[11, :] - np.median(d, axis=0)).sum() == 0

    d_start = pad_along_axis(d, 12, "start", 1, mode="median")
    assert d_start.shape[1] == 12
    assert (d_start[:, 0] - np.median(d, axis=1)).sum() == 0

    d_both = pad_along_axis(d, 12, "both", 1, mode="median")
    assert d_both.shape[1] == 12
    assert (d_both[:, 0] - np.median(d, axis=1)).sum() == 0
    assert (d_both[:, -1] - np.median(d, axis=1)).sum() == 0

    d_same = pad_along_axis(d, 9, "end", 0, mode="median")
    assert (d_same - d).sum() == 0


def test_crop():
    d = np.random.random((10, 10))
    try:
        crop(d, 2, 20, 0)
    except OverflowError:
        pass

    d2 = crop(d, 2, 4, 0)
    assert d2.shape[0] == 4

    d3 = crop(d, 2, 4, 1)
    assert d3.shape[1] == 4

    d_same = crop(d, 2, 10, 1)
    assert (d_same - d).sum() == 0


def test_myencoder():
    c = MyEncoder()
    t = {}
    t["1"] = np.int(1)
    t["2"] = np.float(2)
    t["3"] = np.array([1, 2])
    t["4"] = 1
    t["5"] = "a"

    with open("test.json", "w") as fp:
        json.dump(t, fp, cls=MyEncoder, indent=4)

    assert os.path.isfile("test.json")
    os.remove("test.json")
