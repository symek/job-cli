from .base import BaseSubCommand

class CreateJobTemplate(BaseSubCommand):
    """ Sub command which performs creation of disk directories
       based on schemas.
    """
 
    def create_command(self):  
        """
        """
        def parse_asset_name(name):
            """ Parse asset name or asset group for patterns asset[1-2]
            """
            import re
            expression = re.compile('\[([0-9]+)-([0-9]+)\]$')
            sequence   = expression.findall(name)
            if sequence:
                return [int(x) for x in list(sequence[0])]
            return []

        def create_job_asset_range(job_asset_name, number_mult=10, zeros=4):
            """ Generates a list of asset names from asset name expression:
                asset_name[1-10]

                Params:
                    asset_name = 'shot[1-10]' ('shot0010' which won't be expanded.)

                Returns:
                    list = [base0010, base0020, ....]
            """
            job_asset_name_list = []
            job_asset_range = parse_asset_name(job_asset_name)
            assert not job_asset_range or len(job_asset_range) == 2

            # !!! inclusive 
            if len(job_asset_range) == 2:
                job_asset_range[1] += 1 # !!!

            if job_asset_range:
                job_asset_base = job_asset_name.split("[")[0] # Correct assumption?
                for asset_num in range(*job_asset_range):
                    # Should we allow to customize it? Place for preferences?
                    asset_num *= number_mult
                    new_job_asset_name = job_asset_base + str(asset_num).zfill(zeros)
                    job_asset_name_list += [new_job_asset_name]

            else:
                job_asset_name_list += [job_asset_name]

            return job_asset_name_list
            

        from job.template import JobTemplate
        from job.utils import setup_logger, get_log_level_from_options
        from os import environ
        log_level = get_log_level_from_options(self.cli_options)

        job_current    = self.cli_options['PROJECT']
        job_asset_type = self.cli_options['TYPE']
        job_asset_name = self.cli_options['ASSET']

        if self.cli_options['--root']:
            root = self.cli_options['--root']
        else:
            root = None

        if not job_asset_type or not job_asset_name:
            job_asset_type = job_current
            job_asset_name = job_current


        # Pack arguments so we can ommit None one (like root):
        kwargs = {}
        kwargs['job_current']  = job_current
        kwargs['job_asset_type'] = job_asset_type
        kwargs['log_level'] = log_level
        if root:
            kwargs['root']  = root

        # Asset may contain range expression which we might want to expand:
        job_asset_type_range = create_job_asset_range(job_asset_type, number_mult=1, zeros=2)
        job_asset_range = create_job_asset_range(job_asset_name)

        for group in job_asset_type_range:
            kwargs['job_asset_type'] = group
            for asset in job_asset_range:
                kwargs['job_asset_name'] = asset
                job = JobTemplate(**kwargs)
                # We need to reinitialize Job() in case we want to find
                # local schemas:
                if not self.cli_options['--no-local-schema']:
                    local_schema_path = job.get_local_schema_path()
                    job.load_schemas(local_schema_path)
                    super(JobTemplate, job).__init__(job.schema, "job", **kwargs)
                job.create()

        return job
 
    def run(self):
        """ Entry point for sub command.
        """

        if self.cli_options['create']:
            job = self.create_command()
        # FIXME: This is temporary.
        if job and not self.cli_options['--no-local-schema'] and \
        self.cli_options['PROJECT'] and not self.cli_options['TYPE']:
            job.dump_local_templates()







      