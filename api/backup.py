import boto3
import schedule
import time
from datetime import datetime
import os

class DatabaseBackup:
    def __init__(self, app):
        self.app = app
        self.s3 = boto3.client('s3')
        self.bucket = app.config['BACKUP_BUCKET']
    
    def backup_database(self):
        """备份数据库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.sql'
        
        # 导出数据库
        os.system(f'pg_dump {self.app.config["DATABASE_URL"]} > {filename}')
        
        # 上传到S3
        self.s3.upload_file(filename, self.bucket, filename)
        
        # 清理本地文件
        os.remove(filename)
        
        self.app.logger.info(f'数据库备份完成: {filename}')
    
    def restore_database(self, backup_file):
        """恢复数据库"""
        # 从S3下载备份
        self.s3.download_file(self.bucket, backup_file, backup_file)
        
        # 恢复数据库
        os.system(f'psql {self.app.config["DATABASE_URL"]} < {backup_file}')
        
        # 清理文件
        os.remove(backup_file)
        
        self.app.logger.info(f'数据库恢复完成: {backup_file}')
    
    def schedule_backup(self):
        """计划备份任务"""
        schedule.every().day.at("00:00").do(self.backup_database)
        
        while True:
            schedule.run_pending()
            time.sleep(60)