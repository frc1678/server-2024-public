import pymongo

class BaseCalculations:
    def __init__(self, server):
        self.server = server
        self.oplog = self.server.oplog
        self.update_timestamp()
        self.watched_collections = NotImplemented   # Calculations should override this attribute

    def update_timestamp(self):
        """Updates the timestamp to the most recent oplog entry timestamp"""
        last_op = self.oplog.find({}).sort('ts', pymongo.DESCENDING).limit(1)
        self.timestamp = last_op.next()['ts']

    def entries_since_last(self):
        return self.oplog.find(
            {
                'ts': {'$gt': self.timestamp},
                'op': {'$in': ['i', 'd', 'u']},
                'ns': {
                    '$in': [
                        f'{self.server.db.name}.{c}' for c in self.watched_collections
                    ]
                },
            }
        )

    @staticmethod
    def avg(nums, weights=None, default=0):
        """Calculates the average of a list of numeric types.

        If the optional parameter weights is given, calculates a weighted average
        weights should be a list of floats. The length of weights must be the same as the length of nums
        default is the value returned if nums is an empty list
        """
        if len(nums) == 0:
            return default
        if weights is None:
            # Normal (not weighted) average
            return sum(nums) / len(nums)
        # Expect one weight for each number
        if len(nums) != len(weights):
            raise ValueError(f'Weighted average expects one weight for each number.')
        weighted_sum = sum([num * weight for num, weight in zip(nums, weights)])
        return weighted_sum / sum(weights)
