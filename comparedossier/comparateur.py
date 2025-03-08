import sys
import os
import shutil
import filecmp
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QMessageBox, QSplitter, QProgressBar, QCheckBox,
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

class FileOperation(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, source_files, dest_dir, operation="copy"):
        super().__init__()
        self.source_files = source_files
        self.dest_dir = dest_dir
        self.operation = operation  # "copy" ou "move"

    def run(self):
        total_files = len(self.source_files)
        for i, (source, filename) in enumerate(self.source_files):
            try:
                dest_path = os.path.join(self.dest_dir, filename)
                
                if self.operation == "copy":
                    shutil.copy2(source, dest_path)
                elif self.operation == "move":
                    shutil.move(source, dest_path)
                
                # Émettre le signal de progression
                self.progress.emit(int((i + 1) / total_files * 100))
            except Exception as e:
                self.error.emit(f"Erreur lors du traitement de {filename}: {str(e)}")
                
        self.finished.emit()

class DirectoryComparator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Attributs pour stocker les infos des répertoires
        self.directory1 = ""
        self.directory2 = ""
        self.files_info1 = {}  # {filename: {size, mtime, path, status}}
        self.files_info2 = {}
        
    def initUI(self):
        self.setWindowTitle("Comparateur de répertoires amélioré")
        self.resize(900, 600)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Création du splitter horizontal pour diviser l'écran
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche (répertoire 1)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.label1 = QLabel("Répertoire 1: (Taille: 0 Ko)")
        self.selectButton1 = QPushButton("Sélectionner Répertoire 1")
        
        # Utiliser un QTableWidget au lieu de QListWidget
        self.tableWidget1 = QTableWidget()
        self.tableWidget1.setColumnCount(3)
        self.tableWidget1.setHorizontalHeaderLabels(["Nom", "Taille", "Date de modification"])
        self.tableWidget1.setSelectionMode(QTableWidget.MultiSelection)
        self.tableWidget1.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        left_layout.addWidget(self.label1)
        left_layout.addWidget(self.selectButton1)
        left_layout.addWidget(self.tableWidget1)
        
        # Panneau droit (répertoire 2)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.label2 = QLabel("Répertoire 2: (Taille: 0 Ko)")
        self.selectButton2 = QPushButton("Sélectionner Répertoire 2")
        
        self.tableWidget2 = QTableWidget()
        self.tableWidget2.setColumnCount(3)
        self.tableWidget2.setHorizontalHeaderLabels(["Nom", "Taille", "Date de modification"])
        self.tableWidget2.setSelectionMode(QTableWidget.MultiSelection)
        self.tableWidget2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        right_layout.addWidget(self.label2)
        right_layout.addWidget(self.selectButton2)
        right_layout.addWidget(self.tableWidget2)
        
        # Ajouter les panneaux au splitter
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        
        # Panneau inférieur (options et actions)
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Groupe d'options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_subdirs_cb = QCheckBox("Inclure les sous-répertoires")
        self.compare_content_cb = QCheckBox("Comparer le contenu des fichiers")
        self.overwrite_cb = QCheckBox("Écraser les fichiers existants")
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrer par:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous les fichiers", "Fichiers communs", "Fichiers uniques", "Fichiers différents"])
        filter_layout.addWidget(self.filter_combo)
        
        options_layout.addWidget(self.include_subdirs_cb)
        options_layout.addWidget(self.compare_content_cb)
        options_layout.addWidget(self.overwrite_cb)
        options_layout.addLayout(filter_layout)
        
        # Groupe d'actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.copy_1_to_2_btn = QPushButton("Copier de 1 vers 2")
        self.copy_2_to_1_btn = QPushButton("Copier de 2 vers 1")
        self.move_1_to_2_btn = QPushButton("Déplacer de 1 vers 2")
        self.move_2_to_1_btn = QPushButton("Déplacer de 2 vers 1")
        self.refresh_btn = QPushButton("Rafraîchir")
        
        actions_layout.addWidget(self.copy_1_to_2_btn)
        actions_layout.addWidget(self.copy_2_to_1_btn)
        actions_layout.addWidget(self.move_1_to_2_btn)
        actions_layout.addWidget(self.move_2_to_1_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        # Ajouter les groupes au panneau inférieur
        bottom_layout.addWidget(options_group)
        bottom_layout.addWidget(actions_group)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Ajouter tous les éléments au layout principal
        main_layout.addWidget(self.splitter, 7)
        main_layout.addWidget(bottom_panel, 2)
        main_layout.addWidget(self.progress_bar, 1)
        
        self.setLayout(main_layout)
        
        # Connecter les signaux
        self.selectButton1.clicked.connect(self.select_directory1)
        self.selectButton2.clicked.connect(self.select_directory2)
        self.copy_1_to_2_btn.clicked.connect(self.copy_from_1_to_2)
        self.copy_2_to_1_btn.clicked.connect(self.copy_from_2_to_1)
        self.move_1_to_2_btn.clicked.connect(self.move_from_1_to_2)
        self.move_2_to_1_btn.clicked.connect(self.move_from_2_to_1)
        self.refresh_btn.clicked.connect(self.refresh_lists)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        self.include_subdirs_cb.stateChanged.connect(self.refresh_lists)
        self.compare_content_cb.stateChanged.connect(lambda: self.refresh_lists(force_compare=True))
        
    def select_directory1(self):
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner Répertoire 1")
        if directory:
            self.directory1 = directory
            size_str = self.get_directory_size(directory)
            self.label1.setText(f"Répertoire 1: {directory} (Taille: {size_str})")
            self.refresh_lists()
    
    def select_directory2(self):
        directory = QFileDialog.getExistingDirectory(self, "Sélectionner Répertoire 2")
        if directory:
            self.directory2 = directory
            size_str = self.get_directory_size(directory)
            self.label2.setText(f"Répertoire 2: {directory} (Taille: {size_str})")
            self.refresh_lists()
    
    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for file in filenames:
                fp = os.path.join(dirpath, file)
                total_size += os.path.getsize(fp)
        
        return self.format_size(total_size)
    
    def format_size(self, size_bytes):
        size_kb = size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} Ko"
        size_mb = size_kb / 1024
        if size_mb < 1024:
            return f"{size_mb:.2f} Mo"
        size_gb = size_mb / 1024
        return f"{size_gb:.2f} Go"
    
    def format_file_size(self, size_bytes):
        # Format pour l'affichage des tailles de fichiers
        if size_bytes < 1024:
            return f"{size_bytes} o"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} Ko"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} Mo"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} Go"
    
    def refresh_lists(self, force_compare=False):
        """Rafraîchir les deux listes de fichiers"""
        if not self.directory1 or not self.directory2:
            return
        
        self.tableWidget1.clearContents()
        self.tableWidget2.clearContents()
        
        # Récupérer les informations des fichiers
        self.files_info1 = self.get_files_info(self.directory1)
        self.files_info2 = self.get_files_info(self.directory2)
        
        # Comparer les fichiers si demandé
        if self.compare_content_cb.isChecked() or force_compare:
            self.compare_files()
        
        # Appliquer le filtre actuel
        self.apply_filter()
    
    def get_files_info(self, directory):
        """Récupérer les informations des fichiers dans le répertoire"""
        files_info = {}
        
        if self.include_subdirs_cb.isChecked():
            # Inclure les sous-répertoires
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, directory)
                    
                    # Obtenir les infos du fichier
                    stat_info = os.stat(full_path)
                    size = stat_info.st_size
                    mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                    
                    files_info[rel_path] = {
                        'size': size,
                        'mtime': mtime,
                        'path': full_path,
                        'status': 'normal'  # Par défaut
                    }
        else:
            # Uniquement les fichiers du répertoire principal
            for filename in os.listdir(directory):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    # Obtenir les infos du fichier
                    stat_info = os.stat(full_path)
                    size = stat_info.st_size
                    mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                    
                    files_info[filename] = {
                        'size': size,
                        'mtime': mtime,
                        'path': full_path,
                        'status': 'normal'  # Par défaut
                    }
        
        return files_info
    
    def compare_files(self):
        """Comparer les fichiers entre les deux répertoires"""
        # Marquer les fichiers qui n'existent que dans un répertoire
        for filename in self.files_info1:
            if filename not in self.files_info2:
                self.files_info1[filename]['status'] = 'unique'
            else:
                # Comparer les tailles des fichiers
                if self.files_info1[filename]['size'] != self.files_info2[filename]['size']:
                    self.files_info1[filename]['status'] = 'different'
                    self.files_info2[filename]['status'] = 'different'
                elif self.compare_content_cb.isChecked():
                    # Comparer le contenu des fichiers si demandé et si les tailles sont identiques
                    if not filecmp.cmp(self.files_info1[filename]['path'], self.files_info2[filename]['path'], shallow=False):
                        self.files_info1[filename]['status'] = 'different'
                        self.files_info2[filename]['status'] = 'different'
                    else:
                        self.files_info1[filename]['status'] = 'identical'
                        self.files_info2[filename]['status'] = 'identical'
                else:
                    self.files_info1[filename]['status'] = 'identical'
                    self.files_info2[filename]['status'] = 'identical'
        
        for filename in self.files_info2:
            if filename not in self.files_info1:
                self.files_info2[filename]['status'] = 'unique'
    
    def apply_filter(self):
        """Appliquer le filtre sélectionné aux listes de fichiers"""
        filter_option = self.filter_combo.currentText()
        
        # Réinitialiser les tableaux
        self.tableWidget1.clearContents()
        self.tableWidget2.clearContents()
        self.tableWidget1.setRowCount(0)
        self.tableWidget2.setRowCount(0)
        
        # Filtrer et afficher les fichiers du répertoire 1
        filtered_files1 = []
        for filename, info in self.files_info1.items():
            if filter_option == "Tous les fichiers" or \
               (filter_option == "Fichiers communs" and info['status'] == 'identical') or \
               (filter_option == "Fichiers uniques" and info['status'] == 'unique') or \
               (filter_option == "Fichiers différents" and info['status'] == 'different'):
                filtered_files1.append((filename, info))
        
        self.populate_table(self.tableWidget1, filtered_files1)
        
        # Filtrer et afficher les fichiers du répertoire 2
        filtered_files2 = []
        for filename, info in self.files_info2.items():
            if filter_option == "Tous les fichiers" or \
               (filter_option == "Fichiers communs" and info['status'] == 'identical') or \
               (filter_option == "Fichiers uniques" and info['status'] == 'unique') or \
               (filter_option == "Fichiers différents" and info['status'] == 'different'):
                filtered_files2.append((filename, info))
        
        self.populate_table(self.tableWidget2, filtered_files2)
    
    def populate_table(self, table_widget, files):
        """Remplir le tableau avec les fichiers filtrés"""
        table_widget.setRowCount(len(files))
        
        for row, (filename, info) in enumerate(files):
            # Nom du fichier
            name_item = QTableWidgetItem(filename)
            
            # Coloration selon le statut
            if info['status'] == 'unique':
                name_item.setBackground(QBrush(QColor(255, 200, 200)))  # Rouge clair pour unique
            elif info['status'] == 'different':
                name_item.setBackground(QBrush(QColor(255, 255, 200)))  # Jaune clair pour différent
            elif info['status'] == 'identical':
                name_item.setBackground(QBrush(QColor(200, 255, 200)))  # Vert clair pour identique
            
            table_widget.setItem(row, 0, name_item)
            
            # Taille du fichier
            size_item = QTableWidgetItem(self.format_file_size(info['size']))
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table_widget.setItem(row, 1, size_item)
            
            # Date de modification
            date_item = QTableWidgetItem(info['mtime'].strftime("%Y-%m-%d %H:%M"))
            table_widget.setItem(row, 2, date_item)
    
    def get_selected_files(self, table_widget, files_info):
        """Récupérer les fichiers sélectionnés dans un tableau"""
        selected_files = []
        for item in table_widget.selectedItems():
            if item.column() == 0:  # Seulement compter la première colonne
                filename = item.text()
                if filename in files_info:
                    selected_files.append((files_info[filename]['path'], filename))
        return selected_files
    
    def check_conflicts(self, source_files, dest_dir):
        """Vérifier les conflits de nom de fichier avant la copie/déplacement"""
        conflicts = []
        for _, filename in source_files:
            dest_path = os.path.join(dest_dir, filename)
            if os.path.exists(dest_path):
                conflicts.append(filename)
        
        if conflicts and not self.overwrite_cb.isChecked():
            msg = "Les fichiers suivants existent déjà dans le répertoire de destination:\n"
            msg += "\n".join(conflicts)
            msg += "\n\nVoulez-vous écraser ces fichiers?"
            
            reply = QMessageBox.question(self, "Conflit de fichiers", msg, 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def copy_from_1_to_2(self):
        """Copier les fichiers sélectionnés du répertoire 1 vers le répertoire 2"""
        if not self.directory1 or not self.directory2:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux répertoires.")
            return
        
        selected_files = self.get_selected_files(self.tableWidget1, self.files_info1)
        
        if not selected_files:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner des fichiers à copier.")
            return
        
        if not self.check_conflicts(selected_files, self.directory2):
            return
        
        # Lancer l'opération de copie dans un thread séparé
        self.progress_bar.setVisible(True)
        self.file_operation = FileOperation(selected_files, self.directory2, "copy")
        self.file_operation.progress.connect(self.progress_bar.setValue)
        self.file_operation.finished.connect(self.operation_finished)
        self.file_operation.error.connect(self.show_error)
        self.file_operation.start()
    
    def copy_from_2_to_1(self):
        """Copier les fichiers sélectionnés du répertoire 2 vers le répertoire 1"""
        if not self.directory1 or not self.directory2:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux répertoires.")
            return
        
        selected_files = self.get_selected_files(self.tableWidget2, self.files_info2)
        
        if not selected_files:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner des fichiers à copier.")
            return
        
        if not self.check_conflicts(selected_files, self.directory1):
            return
        
        # Lancer l'opération de copie dans un thread séparé
        self.progress_bar.setVisible(True)
        self.file_operation = FileOperation(selected_files, self.directory1, "copy")
        self.file_operation.progress.connect(self.progress_bar.setValue)
        self.file_operation.finished.connect(self.operation_finished)
        self.file_operation.error.connect(self.show_error)
        self.file_operation.start()
    
    def move_from_1_to_2(self):
        """Déplacer les fichiers sélectionnés du répertoire 1 vers le répertoire 2"""
        if not self.directory1 or not self.directory2:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux répertoires.")
            return
        
        selected_files = self.get_selected_files(self.tableWidget1, self.files_info1)
        
        if not selected_files:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner des fichiers à déplacer.")
            return
        
        if not self.check_conflicts(selected_files, self.directory2):
            return
        
        # Lancer l'opération de déplacement dans un thread séparé
        self.progress_bar.setVisible(True)
        self.file_operation = FileOperation(selected_files, self.directory2, "move")
        self.file_operation.progress.connect(self.progress_bar.setValue)
        self.file_operation.finished.connect(self.operation_finished)
        self.file_operation.error.connect(self.show_error)
        self.file_operation.start()
    
    def move_from_2_to_1(self):
        """Déplacer les fichiers sélectionnés du répertoire 2 vers le répertoire 1"""
        if not self.directory1 or not self.directory2:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux répertoires.")
            return
        
        selected_files = self.get_selected_files(self.tableWidget2, self.files_info2)
        
        if not selected_files:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner des fichiers à déplacer.")
            return
        
        if not self.check_conflicts(selected_files, self.directory1):
            return
        
        # Lancer l'opération de déplacement dans un thread séparé
        self.progress_bar.setVisible(True)
        self.file_operation = FileOperation(selected_files, self.directory1, "move")
        self.file_operation.progress.connect(self.progress_bar.setValue)
        self.file_operation.finished.connect(self.operation_finished)
        self.file_operation.error.connect(self.show_error)
        self.file_operation.start()
    
    def operation_finished(self):
        """Appelé lorsqu'une opération de fichier est terminée"""
        self.progress_bar.setVisible(False)
        self.refresh_lists()
        QMessageBox.information(self, "Succès", "Opération terminée avec succès.")
    
    def show_error(self, error_msg):
        """Afficher un message d'erreur"""
        QMessageBox.critical(self, "Erreur", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectoryComparator()
    window.show()
    sys.exit(app.exec_())
