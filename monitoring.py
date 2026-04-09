import time
import psutil
import mysql.connector
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='system_monitor.log'
)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'breakfast_system'
}

class SystemMonitor:
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    def get_system_metrics(self):
        """获取系统资源使用情况"""
        try:
            # CPU使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_used_percent = memory.percent
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_used_percent = disk.percent
            
            # 网络情况
            net_io = psutil.net_io_counters()
            
            self.metrics['system'] = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory_used_percent,
                'disk_usage': disk_used_percent,
                'network_sent': net_io.bytes_sent,
                'network_recv': net_io.bytes_recv
            }
            
            # 检查系统资源使用情况
            self.check_system_resources()
            
        except Exception as e:
            logging.error(f'获取系统指标失败: {e}')
    
    def check_database_connection(self):
        """检查数据库连接状态"""
        try:
            start_time = time.time()
            conn = mysql.connector.connect(**DB_CONFIG)
            end_time = time.time()
            
            if conn.is_connected():
                connection_time = (end_time - start_time) * 1000  # 转换为毫秒
                self.metrics['database'] = {
                    'status': 'connected',
                    'connection_time_ms': connection_time,
                    'timestamp': datetime.now().isoformat()
                }
                conn.close()
            else:
                self.metrics['database'] = {
                    'status': 'disconnected',
                    'timestamp': datetime.now().isoformat()
                }
                self.alerts.append({
                    'level': 'ERROR',
                    'message': '数据库连接失败',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            self.metrics['database'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append({
                'level': 'ERROR',
                'message': f'数据库连接错误: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
            logging.error(f'数据库连接检查失败: {e}')
    
    def check_system_resources(self):
        """检查系统资源使用情况，生成预警"""
        system_metrics = self.metrics.get('system', {})
        
        # CPU使用预警
        cpu_usage = system_metrics.get('cpu_usage', 0)
        if cpu_usage > 80:
            self.alerts.append({
                'level': 'WARNING',
                'message': f'CPU使用率过高: {cpu_usage}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # 内存使用预警
        memory_usage = system_metrics.get('memory_usage', 0)
        if memory_usage > 80:
            self.alerts.append({
                'level': 'WARNING',
                'message': f'内存使用率过高: {memory_usage}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # 磁盘使用预警
        disk_usage = system_metrics.get('disk_usage', 0)
        if disk_usage > 90:
            self.alerts.append({
                'level': 'ERROR',
                'message': f'磁盘使用率过高: {disk_usage}%',
                'timestamp': datetime.now().isoformat()
            })
    
    def get_metrics(self):
        """获取所有监控指标"""
        self.get_system_metrics()
        self.check_database_connection()
        
        return {
            'metrics': self.metrics,
            'alerts': self.alerts
        }
    
    def clear_alerts(self):
        """清空预警信息"""
        self.alerts = []
    
    def get_status_summary(self):
        """获取系统状态摘要"""
        self.get_metrics()
        
        # 检查是否有错误级别的预警
        has_errors = any(alert['level'] == 'ERROR' for alert in self.alerts)
        
        # 检查是否有警告级别的预警
        has_warnings = any(alert['level'] == 'WARNING' for alert in self.alerts)
        
        if has_errors:
            status = 'ERROR'
        elif has_warnings:
            status = 'WARNING'
        else:
            status = 'OK'
        
        return {
            'status': status,
            'alerts_count': len(self.alerts),
            'errors_count': sum(1 for alert in self.alerts if alert['level'] == 'ERROR'),
            'warnings_count': sum(1 for alert in self.alerts if alert['level'] == 'WARNING')
        }

# 创建全局监控实例
monitor = SystemMonitor()

def get_monitor():
    """获取监控实例"""
    return monitor
