

from dlsmith.runTimeInformation.base_run_time import RunTimeBase

class FlixRunTime(RunTimeBase):

    def import_run_time_data(self):
        """
            Import run time data.
        """
        self.logger.add_log_text("\n[FlixRunTime] Importing run time data for Flix")

