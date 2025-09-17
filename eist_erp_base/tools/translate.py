# -*- coding: utf-8 -*-

import logging
from odoo.tools.translate import (
    _get_lang,
    TarFileWriter,
    TranslationFileReader,
    TranslationFileWriter,
    _,
    CSVFileReader,
    PoFileReader,
)
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def safe_translation_file_reader(source, fileformat="po"):
    """
    安全的翻译文件读取器，避免在翻译系统初始化期间的循环依赖问题

    这个函数是对原始 TranslationFileReader 的包装，用于处理在翻译系统
    未完全初始化时可能出现的循环依赖问题。
    """
    try:
        return TranslationFileReader(source, fileformat)
    except Exception as e:
        # 如果翻译系统未完全初始化，使用原始字符串而不是翻译
        if "no translation language detected" in str(e):
            _logger.warning("Translation system not fully initialized, using original strings")
            # 返回一个简化的读取器，不使用翻译功能
            return _SafeTranslationFileReader(source, fileformat)
        raise


def safe_translation_file_writer(target, fileformat="po", lang=None):
    """
    安全的翻译文件写入器，避免在翻译系统初始化期间的循环依赖问题
    """
    try:
        return TranslationFileWriter(target, fileformat, lang)
    except Exception as e:
        if "no translation language detected" in str(e):
            _logger.warning("Translation system not fully initialized, using original strings")
            return _SafeTranslationFileWriter(target, fileformat, lang)
        raise


def safe_user_error(message, *args):
    """
    安全的用户错误创建函数，避免在翻译系统初始化期间的循环依赖问题
    """
    try:
        # 尝试使用翻译

        if args:
            return UserError(_(message) % args)
        else:
            return UserError(_(message))
    except Exception:
        # 如果翻译失败，使用原始字符串
        _logger.debug("Translation failed, using original string: %s", message)
        if args:
            return UserError(message % args)
        else:
            return UserError(message)


class _SafeTranslationFileReader:
    """
    安全的翻译文件读取器，在翻译系统未完全初始化时使用
    """

    def __init__(self, source, fileformat="po"):
        self.source = source
        self.fileformat = fileformat
        self._reader = None
        self._init_reader()

    def _init_reader(self):
        """初始化读取器，不使用翻译功能"""
        try:
            # 直接使用原始实现，但不依赖翻译系统
            if self.fileformat == "csv":
                self._reader = CSVFileReader(self.source)
            elif self.fileformat == "po":
                self._reader = PoFileReader(self.source)
            else:
                raise Exception(f"Bad file format: {self.fileformat}")
        except Exception as e:
            _logger.error("Failed to initialize translation file reader: %s", e)
            raise Exception(f"Bad file format: {self.fileformat}")

    def __iter__(self):
        """迭代翻译条目"""
        if self._reader:
            for entry in self._reader:
                yield entry


class _SafeTranslationFileWriter:
    """
    安全的翻译文件写入器，在翻译系统未完全初始化时使用
    """

    def __init__(self, target, fileformat="po", lang=None):
        self.target = target
        self.fileformat = fileformat
        self.lang = lang
        self._writer = None
        self._init_writer()

    def _init_writer(self):
        """初始化写入器，不使用翻译功能"""
        try:
            if self.fileformat == "csv":
                self._writer = CSVFileWriter(self.target)
            elif self.fileformat == "po":
                self._writer = PoFileWriter(self.target, self.lang)
            elif self.fileformat == "tgz":
                self._writer = TarFileWriter(self.target, self.lang)
            else:
                raise Exception(
                    f"Unrecognized extension: must be one of .csv, .po, or .tgz (received .{self.fileformat})."
                )
        except Exception as e:
            _logger.error("Failed to initialize translation file writer: %s", e)
            raise Exception(
                f"Unrecognized extension: must be one of .csv, .po, or .tgz (received .{self.fileformat})."
            )

    def write_rows(self, rows):
        """写入翻译行"""
        if self._writer:
            self._writer.write_rows(rows)


# 导出修复后的函数，供其他模块使用
__all__ = ["safe_translation_file_reader", "safe_translation_file_writer", "safe_user_error", "_get_lang"]
