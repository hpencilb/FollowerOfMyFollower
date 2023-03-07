from DatabaseTools import DatabaseGuard
from ProcessRelation import RelationProcessor
from SinaFollowerCrawler import Crawler


def get_next_layer(root_uid, is_main=False):
    print(f"getting followers of {root_uid}")
    if not db_guard.select_crawled(root_uid):
        this_layer = crawler.get_user_followers(root_uid, is_main=is_main)
        for follower_tuple in this_layer:
            uid, fnick = follower_tuple
            db_guard.add_user(uid, fnick)
            db_guard.add_relation(root_uid, uid)
        db_guard.set_crawled(root_uid)
        next_layer = [f[0] for f in this_layer]
    else:
        this_layer = db_guard.select_relations_by_uid(root_uid)
        next_layer = [f[1] for f in this_layer]
    return next_layer


def get_two_layer_from_root(root_id):
    db_guard.add_user(root_id, "MASTER")
    first_layer = get_next_layer(root_id, is_main=True)
    for first_layer_id in first_layer:
        second_layer = get_next_layer(first_layer_id)
        for second_layer_id in second_layer:
            get_next_layer(second_layer_id)


if __name__ == '__main__':
    crawler = Crawler()
    db_guard = DatabaseGuard()
    master_id = #FIXME
    get_two_layer_from_root(master_id)
    rl_processor = RelationProcessor(db_guard)
    rl_processor.make_obsidian_database(True, True)
