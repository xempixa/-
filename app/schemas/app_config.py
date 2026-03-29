from __future__ import annotations

from pydantic import BaseModel, Field


class CreatorConfig(BaseModel):
    uid: int
    name: str | None = None
    enabled: bool = True
    sync_dynamics: bool = True
    sync_videos: bool = True
    sync_comments: bool = False
    dynamic_pages: int = 1
    video_pages: int = 1


class CreatorsFile(BaseModel):
    creators: list[CreatorConfig] = Field(default_factory=list)


class DownloadConfig(BaseModel):
    worker_batch_size: int = 3
    max_parallel_downloads: int = 1
    default_priority: int = 100


class RetryConfig(BaseModel):
    enabled: bool = True
    base_delay_seconds: int = 300
    max_delay_seconds: int = 86400
    jitter_seconds: int = 60


class ExportConfig(BaseModel):
    report_dir: str = "./reports"
    include_raw_json: bool = False


class RuntimeConfig(BaseModel):
    single_instance_lock: bool = True
    save_run_log: bool = True


class AppConfigFile(BaseModel):
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
