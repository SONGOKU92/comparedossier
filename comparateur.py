import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QMessageBox
)

class DirectoryComparator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparateur de dossiers")
        
        self.layout = QVBoxLayout()
        
        
        self.label1 = QLabel("Dossier 1: (Taille: 0 Ko)")
        self.label2 = QLabel("Dossier 2: (Taille: 0 Ko)")
        
        self.listWidget1 = QListWidget()
        self.listWidget2 = QListWidget()
        
      
        self.listWidget1.setSelectionMode(QListWidget.MultiSelection)
        self.listWidget2.setSelectionMode(QListWidget.MultiSelection)
        
        
        self.selectButton1 = QPushButton("Sélectionner Dossier 1")
        self.selectButton2 = QPushButton("Sélectionner Dossier 2")
        self.copyButton = QPushButton("Copier")
        
       
        self.selectButton1.clicked.connect(self.select_directory1)
        self.selectButton2.clicked.connect(self.select_directory2)
        self.copyButton.clicked.connect(self.copy_selected_files)

        
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.listWidget1)
        self.layout.addWidget(self.selectButton1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.listWidget2)
        self.layout.addWidget(self.selectButton2)
        self.layout.addWidget(self.copyButton)
        
        self.setLayout(self.layout)
    
    def select_directory1(self):
        self.directory1 = QFileDialog.getExistingDirectory(self, "Sélectionner Dossier 1")
        if self.directory1:
            size_str = self.get_directory_size(self.directory1)
            self.label1.setText(f"Dossier 1: {self.directory1} (Taille: {size_str})")
            self.populate_list(self.listWidget1, self.directory1)

    def select_directory2(self):
        self.directory2 = QFileDialog.getExistingDirectory(self, "Sélectionner Dossier 2")
        if self.directory2:
            size_str = self.get_directory_size(self.directory2)
            self.label2.setText(f"Dossier 2: {self.directory2} (Taille: {size_str})")
            self.populate_list(self.listWidget2, self.directory2)
    
    def populate_list(self, list_widget, directory):
        list_widget.clear()
        for item in os.listdir(directory):
            list_widget.addItem(item)
    
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

    def copy_selected_files(self):
        
        if not hasattr(self, 'directory1') or not hasattr(self, 'directory2'):
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux dossiers.")
            return
        
       
        selected_items1 = self.listWidget1.selectedItems()
        selected_items2 = self.listWidget2.selectedItems()

        copied = False
        
      
        if selected_items1:
            for item in selected_items1:
                file_to_copy = os.path.join(self.directory1, item.text())
                shutil.copy(file_to_copy, self.directory2)
            copied = True
        
       
        if selected_items2:
            for item in selected_items2:
                file_to_copy = os.path.join(self.directory2, item.text())
                shutil.copy(file_to_copy, self.directory1)
            copied = True

        if copied:
            QMessageBox.information(self, "Succès", "Fichiers copiés avec succès.")
            QApplication.quit()  
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner des fichiers à copier.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectoryComparator()
    window.show()
    sys.exit(app.exec_())
