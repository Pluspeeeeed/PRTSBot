from op import Operator


class Gacha:
    def __init__(self, start_time, end_time, filename, pickup_op, *, shop_op=None, link=None):
        if shop_op is None:
            shop_op = []
        if link is None:
            link = ""
        self.start_time = start_time
        self.end_time = end_time
        self.filename = filename
        self.pickup_op = pickup_op
        self.shop_op = shop_op
        self.link = link

        for op in shop_op:
            pickup_op.remove(op)

    def show(self):
        print(self.filename)
        print(f"start time: {self.start_time}")
        print(f"end time: {self.end_time}")
        print(f"shop:")
        for op in self.shop_op:
            print(f"{op}, ")
        print(f"pickup:")
        for op in self.shop_op:
            print(f"{op},")
        for op in self.pickup_op:
            print(f"{op},")
