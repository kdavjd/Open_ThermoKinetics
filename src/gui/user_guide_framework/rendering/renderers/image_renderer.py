"""
Image Renderer - Рендерер для изображений и медиа контента
"""

from pathlib import Path
from typing import Any, Dict, List

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .base_renderer import BaseRenderer


class ImageRenderer(BaseRenderer):
    """
    Рендерер для изображений, GIF анимаций и видео контента.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов медиа контента."""
        return ["image", "gif", "video", "gallery", "diagram"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит медиа контент в соответствующий виджет.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный медиа виджет
        """
        content_type = content.get("type")
        content_data = content.get("content", {})

        if content_type == "image":
            return self._render_image(content_data)
        elif content_type == "gif":
            return self._render_gif(content_data)
        elif content_type == "video":
            return self._render_video_placeholder(content_data)
        elif content_type == "gallery":
            return self._render_gallery(content_data)
        elif content_type == "diagram":
            return self._render_diagram(content_data)
        else:
            return self._render_placeholder(f"Unsupported media type: {content_type}")

    def _render_image(self, image_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет изображения.

        Args:
            image_data: Данные изображения (path, caption, width, height)

        Returns:
            QWidget: Виджет с изображением
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        # Загружаем изображение
        image_path = image_data.get("path", "")
        caption = image_data.get("caption", "")
        max_width = image_data.get("max_width", 500)
        max_height = image_data.get("max_height", 400)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if image_path and Path(image_path).exists():
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Масштабируем изображение с сохранением пропорций
                scaled_pixmap = pixmap.scaled(
                    QSize(max_width, max_height),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("❌ Не удалось загрузить изображение")
        else:
            image_label.setText("❌ Изображение не найдено")

        # Стилизация изображения
        image_label.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {self.get_theme_color("border")};
                border-radius: 4px;
                padding: 4px;
                background-color: {self.get_theme_color("surface")};
                margin: 8px 0px;
            }}
        """)

        layout.addWidget(image_label)

        # Добавляем подпись если есть
        if caption:
            caption_label = QLabel(caption)
            caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption_label.setWordWrap(True)

            font = self.get_theme_font("body")
            if font:
                font.setItalic(True)
                caption_label.setFont(font)

            caption_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_secondary")};
                    font-style: italic;
                    padding: 4px 8px;
                    margin-bottom: 8px;
                }}
            """)

            layout.addWidget(caption_label)

        return container

    def _render_gif(self, gif_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет анимированного GIF.

        Args:
            gif_data: Данные GIF анимации

        Returns:
            QWidget: Виджет с анимацией
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        gif_path = gif_data.get("path", "")
        caption = gif_data.get("caption", "")
        auto_play = gif_data.get("auto_play", True)

        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if gif_path and Path(gif_path).exists():
            movie = QMovie(gif_path)
            if movie.isValid():
                gif_label.setMovie(movie)
                if auto_play:
                    movie.start()

                # Контролы для GIF
                controls_layout = QHBoxLayout()

                play_button = QPushButton("▶️ Play")
                pause_button = QPushButton("⏸️ Pause")
                stop_button = QPushButton("⏹️ Stop")

                play_button.clicked.connect(movie.start)
                pause_button.clicked.connect(movie.setPaused)
                stop_button.clicked.connect(movie.stop)

                controls_layout.addWidget(play_button)
                controls_layout.addWidget(pause_button)
                controls_layout.addWidget(stop_button)

                layout.addWidget(gif_label)
                layout.addLayout(controls_layout)
            else:
                gif_label.setText("❌ Не удалось загрузить GIF анимацию")
                layout.addWidget(gif_label)
        else:
            gif_label.setText("❌ GIF файл не найден")
            layout.addWidget(gif_label)

        # Добавляем подпись
        if caption:
            caption_label = QLabel(caption)
            caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption_label.setWordWrap(True)
            layout.addWidget(caption_label)

        return container

    def _render_video_placeholder(self, video_data: Dict[str, Any]) -> QWidget:
        """
        Создает placeholder для видео (пока без полной поддержки видео).

        Args:
            video_data: Данные видео

        Returns:
            QWidget: Placeholder виджет
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = video_data.get("title", "Видео")
        description = video_data.get("description", "")

        # Placeholder изображение
        placeholder = QLabel("🎥 Видео контент\n(Будет реализовано)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {self.get_theme_color("border")};
                border-radius: 8px;
                padding: 40px;
                background-color: {self.get_theme_color("surface")};
                color: {self.get_theme_color("text_secondary")};
                font-size: 14px;
            }}
        """)

        layout.addWidget(QLabel(f"<b>{title}</b>"))
        layout.addWidget(placeholder)

        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        return container

    def _render_gallery(self, gallery_data: Dict[str, Any]) -> QWidget:
        """
        Создает галерею изображений.

        Args:
            gallery_data: Данные галереи

        Returns:
            QWidget: Виджет галереи
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = gallery_data.get("title", "")
        images = gallery_data.get("images", [])

        if title:
            title_label = QLabel(f"<b>{title}</b>")
            layout.addWidget(title_label)

        # Создаем сетку изображений
        images_layout = QHBoxLayout()

        for image_info in images[:4]:  # Ограничиваем до 4 изображений
            image_widget = self._render_image(image_info)
            image_widget.setMaximumWidth(150)
            images_layout.addWidget(image_widget)

        if len(images) > 4:
            more_label = QLabel(f"... и еще {len(images) - 4} изображений")
            more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            images_layout.addWidget(more_label)

        layout.addLayout(images_layout)
        return container

    def _render_diagram(self, diagram_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет диаграммы или схемы.

        Args:
            diagram_data: Данные диаграммы

        Returns:
            QWidget: Виджет диаграммы
        """
        # Пока используем базовый рендер изображения
        return self._render_image(diagram_data)

    def _render_placeholder(self, message: str) -> QWidget:
        """
        Создает placeholder виджет с сообщением.

        Args:
            message: Сообщение для отображения

        Returns:
            QWidget: Placeholder виджет
        """
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {self.get_theme_color("border")};
                border-radius: 4px;
                padding: 20px;
                background-color: {self.get_theme_color("surface")};
                color: {self.get_theme_color("text_secondary")};
            }}
        """)
        return placeholder
