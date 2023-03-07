import os.path

from DatabaseTools import DatabaseGuard


class RelationProcessor:
    def __init__(self, database_guard, has_tier1=False, has_tier2=False):
        self.dbg = database_guard
        self.has_tier1 = has_tier1
        self.has_tier2 = has_tier2

    def update_tier1_count(self):
        total_count = len(self.dbg.select_uid())
        counter = 0
        for uid, in self.dbg.select_uid():
            self.dbg.update_relations_by_uid(uid, len(self.dbg.select_relations_by_uid(uid)))
            counter += 1
            print(f"Tier1 progress: {counter}/{total_count}", flush=True)
        self.has_tier1 = True

    def update_tier2_count(self):
        if not self.has_tier1:
            self.update_tier1_count()
        tier1_users = self.get_tier1_users()
        total_count = len(tier1_users)
        counter = 0
        for uid in tier1_users:
            self.dbg.update_real_relations_by_uid(uid, len([r[1] for r in self.dbg.select_relations_by_uid(uid) if
                                                            r[1] in tier1_users]))
            counter += 1
            print(f"Tier2 progress: {counter}/{total_count}", flush=True)
        self.has_tier2 = True

    def get_tier1_users(self):
        if not self.has_tier1:
            self.update_tier1_count()
        user_ids = self.dbg.select_tier1_uid()
        uids = [u[0] for u in user_ids]
        return set(uids)

    def get_tier2_users(self):
        if not self.has_tier2:
            self.update_tier2_count()
        user_ids = self.dbg.select_tier2_uid()
        uids = [u[0] for u in user_ids]
        return set(uids)

    def write_obsidian(self, uids, tier):
        if not os.path.exists('obsidian' + os.sep + tier):
            os.mkdir('obsidian' + os.sep + tier)
        total_count = len(uids)
        counter = 0
        for uid in uids:
            relations = self.dbg.select_relations_by_uid(uid)
            lines = [f'[[{r[1]}.md]]\n' for r in relations if r[1] in uids]
            with open('obsidian' + os.sep + tier + os.sep + f'{uid}.md', 'w+') as f:
                f.writelines(lines)
            counter += 1
            print(f"Write {tier} obsidian progress: {counter}/{total_count}", flush=True)

    def make_obsidian_database(self, tier1=False, tier2=False):
        if not os.path.exists('obsidian'):
            os.mkdir('obsidian')
        if tier1 and not self.has_tier1:
            self.update_tier1_count()
        if tier1:
            tier1_users = self.get_tier1_users()
            self.write_obsidian(tier1_users, "tier1")
        if tier2 and not self.has_tier2:
            self.update_tier2_count()
        if tier2:
            tier2_users = self.get_tier2_users()
            self.write_obsidian(tier2_users, "tier2")


if __name__ == '__main__':
    db_guard = DatabaseGuard()
    rl_processor = RelationProcessor(db_guard, True, True)
    rl_processor.make_obsidian_database(True, True)
