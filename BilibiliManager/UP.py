import os
from bilibili_api import user
from BilibiliManager.post_video import PostVideoDownloader
from BilibiliManager.live_record import LiveRecordDownloader
from BilibiliManager.public import check_path


class UPTask:
    def __init__(self, download_script_repo, logger, upper_repo, info):
        self.download_script_repo = download_script_repo
        self.live = info.get('live')
        self.custom = info.get('custom')
        self.up = UPInfo(info.get('uid'))
        self.repo = os.path.join(upper_repo, '{}-{}'.format(self.up.uid, self.up.name))
        self.logger = logger

    def main(self):
        check_path(folder_path='./log')
        self.logger.info(f'UP主:{self.up.name} uid:{self.up.uid} live_url:{self.up.live_url}')
        if self.custom:
            PostVideoDownloader(download_script_repo=self.download_script_repo, logger=self.logger,
                                upper_repo=self.repo, up=self.up).main()

        if self.live:
            LiveRecordDownloader(download_script_repo=self.download_script_repo, logger=self.logger,
                                 upper_repo=self.repo, up=self.up).main()


class UPInfo:
    def __init__(self, uid):
        self.uid = int(uid)
        self.name = user.get_user_info(uid=self.uid).get('name')
        self.live_url = user.get_live_info(uid=self.uid).get('url')
