import datetime
import logging
import sys
import time
from subprocess import Popen
from da_base import DaBase


class DaScheduler(DaBase):
    def __init__(self, file_name: str = None):
        super().__init__(file_name)
        self.active = self.config.scheduler.active
        self.scheduler_tasks = {
            entry.time: entry.action for entry in self.config.scheduler.schedule
        }
        self.start_early_seconds = self.config.scheduler.start_early_seconds
        logging.info(
            "Scheduler start early seconds from options.json: %s",
            self.start_early_seconds,
        )

    def run_task_process(self, key_task):
        run_task = self.tasks[key_task]
        proc = Popen(run_task["cmd"])
        proc.wait()
        if proc.returncode != 0 and proc.returncode is not None:
            print(f"Task {key_task} crashed with exit code {proc.returncode}")
            return False
        return True

    def scheduler(self):
        # if not (self.notification_entity is None) and self.notification_opstarten:
        #     self.set_value(self.notification_entity, "DAO scheduler gestart " +
        #                    datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

        while True:
            t = datetime.datetime.now()
            next_min = t.replace(second=0, microsecond=0) + datetime.timedelta(
                minutes=1
            )
            start_at = next_min - datetime.timedelta(
                seconds=self.start_early_seconds
            )
            wait_until = max(start_at, next_min) if start_at <= t else start_at
            time.sleep(max(0, (wait_until - t).total_seconds()))
            logging.info(
                "Scheduler timing: now=%s, scheduled=%s, start_at=%s, wait_until=%s, early_seconds=%s",
                t.strftime("%Y-%m-%d %H:%M:%S"),
                next_min.strftime("%Y-%m-%d %H:%M:%S"),
                start_at.strftime("%Y-%m-%d %H:%M:%S"),
                wait_until.strftime("%Y-%m-%d %H:%M:%S"),
                self.start_early_seconds,
            )
            if not self.active:
                continue
            hour = next_min.hour
            minute = next_min.minute
            key0 = str(hour).zfill(2) + str(minute).zfill(2)
            # ieder uur in dezelfde minuut voorbeeld xx15
            key1 = "xx" + str(minute).zfill(2)
            # iedere minuut in een uur voorbeeld 02xx
            key2 = str(hour).zfill(2) + "xx"
            tasks = []
            for key in self.scheduler_tasks:
                if key == key0:
                    tasks.append(self.scheduler_tasks[key])
                elif key == key1:
                    tasks.append(self.scheduler_tasks[key])
                elif key == key2:
                    tasks.append(self.scheduler_tasks[key])
            for task in tasks:
                for key_task in self.tasks:
                    if self.tasks[key_task]["function"] == task:
                        try:
                            self.run_task_process(key_task)
                        except KeyboardInterrupt:
                            sys.exit()
                            pass
                        except Exception as e:
                            print(e)
                            continue
                        break


def main():
    da_sched = DaScheduler("../data/options.json")
    da_sched.scheduler()


if __name__ == "__main__":
    main()
