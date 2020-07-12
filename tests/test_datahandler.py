import elv


class TestStatistics:
    dh = elv.datahandler.DataHandler()
    assert dh.min("2018-10-11", "2018-11-02") == 3.38
    assert dh.max("2018-10-11", "2018-11-02") == 17.99
    assert dh.mean("2018-10-11", "2018-11-02") == 7.23
    assert dh.sum("2018-10-11", "2018-11-02") == 141.98
