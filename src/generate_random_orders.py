import json
import random
import utils
import logging

log = logging.getLogger(__name__)

scout_orders = set()
id_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

while len(scout_orders) < 200:
    random.shuffle(id_list)
    scout_orders.add(tuple(id_list))

order_dict = {}
order_num = 1

for order in scout_orders:
    order_dict[order_num] = list(order)
    order_num += 1

log.info(order_dict)

with open(utils.create_file_path("data/scout_orders.json"), "w") as file:
    json.dump(order_dict, file)
