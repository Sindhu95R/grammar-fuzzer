from kitty.data.report import Report
import six
from base64 import b64encode
from binascii import Error


class UnixFuzzerReport(Report):
    def __init__(self, name):
        super().__init__(name)

    @staticmethod
    def try_b64encode(data_in):
        try:
            return b64encode(data_in)
        except (TypeError, Error):
            return data_in

    def to_dict(self, encoding='base64'):
        result = dict()
        for k, v in self._data_fields.items():
            if isinstance(v, (bytes, bytearray, six.string_types)):
                v = self.try_b64encode(v)
            result[k] = v

        for k, v in self._sub_reports.items():
            result[k] = v.to_dict(encoding)

        return result
