

from dlsmith.runTimeInformation.base_run_time import RunTimeBase

class DDlogRunTime(RunTimeBase):

    def import_run_time_data(self):
        """
            Import run time data.
        """
        self.logger.add_log_text("\n[DDlogRunTime] Importing run time data for DDLOG")


