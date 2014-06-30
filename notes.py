from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import sys

class Form(QDialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        titleLabel = QLabel("&Title")
        self.titleEdit = QLineEdit("")
        titleLabel.setBuddy(self.titleEdit)
        noteLabel = QLabel("&Note")
        self.noteText = QTextEdit()
        noteLabel.setBuddy(self.noteText)
        authorLabel = QLabel("&Author")
        self.authorEdit = QLineEdit("")
        authorLabel.setBuddy(self.authorEdit)

        self.acceptButton = QPushButton("&Save")
        self.resetButton = QPushButton("&Reset")
        self.deleteButton = QPushButton("&Del")
        self.deleteButton.setIcon(QIcon("./images/delete.png"))
        self.prevButton = QPushButton()
        self.prevButton.setIcon(QIcon("./images/prev.png"))
        self.nextButton = QPushButton()
        self.nextButton.setIcon(QIcon("./images/next.png"))

        layout = QGridLayout()
        layout.addWidget(titleLabel,0,0)
        layout.addWidget(self.titleEdit,0,1,1,4)
        layout.addWidget(noteLabel,1,0)
        layout.addWidget(self.noteText,1,1,5,4)
        layout.addWidget(authorLabel,6,0)
        layout.addWidget(self.authorEdit,6,1,1,4)
        layout.addWidget(self.prevButton,7,0)
        layout.addWidget(self.acceptButton,7,1)
        layout.addWidget(self.deleteButton,7,2)
        layout.addWidget(self.resetButton,7,3)
        layout.addWidget(self.nextButton,7,4)
        self.setLayout(layout)

        self.resetButton.clicked.connect(self.resetUi)
        self.acceptButton.clicked.connect(self.acceptUi)
        self.deleteButton.clicked.connect(self.deleteNote)
        self.prevButton.clicked.connect(self.prevClick)
        self.nextButton.clicked.connect(self.nextClick)
        self.setWindowTitle("Notify")

        # load previous notes on start
        self.load_initial()

    def load_initial(self):
        query.exec_("SELECT id,title,note,author FROM notes")
        if query.first() == False:
            return
        title = query.value(1).toString()
        note = query.value(2).toString()
        author = query.value(3).toString()
        self.titleEdit.setText(title)
        self.noteText.setText(note)
        self.authorEdit.setText(author)
        self.titleEdit.setFocus()
        self.nextButton.setEnabled(True)
        self.prevButton.setEnabled(True)



    def resetUi(self):
        self.titleEdit.clear()
        self.noteText.clear()
        self.authorEdit.clear()

    def acceptUi(self):
        title_text = self.titleEdit.text()
        note_text = self.noteText.toPlainText()
        author_text = self.authorEdit.text()
        print title_text, note_text, author_text
        query.prepare("INSERT INTO notes (title,note,author) VALUES(?,?,?)")
        query.addBindValue(QVariant(QString(title_text)))
        query.addBindValue(QVariant(QString(note_text)))
        query.addBindValue(QVariant(QString(author_text)))
        query.exec_()
        query.exec_("SELECT id,title,note,author FROM notes")
        query.last()
        
    
    def deleteNote(self):
        if query.at() < 0:
            return
        current_id = query.value(0).toInt()[0]
        fallback_id = None
        ''' If there's just 1 row, clear text in app.
            If this is not the 1st entry, fall back on the prev one.
            If this is the 1st entry, fall back on the next one '''
        if (query.seek(-1,relative=True) == False) and (query.seek(1,relative=True) == False):
            self.titleEdit.clear()
            self.noteText.clear()
            self.authorEdit.clear()
        else:
            fallback_id = query.at()
            print "Fallback id " + str(fallback_id)
            print "Current id " + str(current_id)
            title_text = query.value(1).toString()
            note = query.value(2).toString()
            author = query.value(3).toString()
            self.titleEdit.setText(title_text)
            self.noteText.setText(note)
            self.authorEdit.setText(author)
            
        query.exec_("DELETE FROM notes WHERE id = " + QString.number(current_id))

        if fallback_id is None:
            pass
        else:
            print fallback_id
            query.exec_("SELECT id,title,note,author FROM NOTES")
            query.seek(fallback_id)


    def prevClick(self):
        self.nextButton.setEnabled(True)
        self.prevButton.setEnabled(True)
        if query.at() < 0:
            self.prevButton.setEnabled(False)
            return
        if query.previous() == False:
            query.next()
            self.prevButton.setEnabled(False)
        print query.at()
        title = query.value(1).toString()
        note = query.value(2).toString()
        author = query.value(3).toString()
        self.titleEdit.setText(title)
        self.noteText.setText(note)
        self.authorEdit.setText(author)
        self.titleEdit.setFocus()

    def nextClick(self):
        self.nextButton.setEnabled(True)
        self.prevButton.setEnabled(True)
        if query.at() < 0:
            self.nextButton.setEnabled(False)
            return
        print query.at()
        if query.next() == False:
            query.previous()
            self.nextButton.setEnabled(False)
        title = query.value(1).toString()
        note = query.value(2).toString()
        author = query.value(3).toString()
        self.titleEdit.setText(title)
        self.noteText.setText(note)
        self.authorEdit.setText(author)
        self.titleEdit.setFocus()
    
        


app = QApplication(sys.argv)
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("notedb")
if not db.open():
    QMessageBox.warning(None,"Notify",QString("Database error: %1").arg(db.lastError().text()))
    sys.exit(1)
query = QSqlQuery()
query.exec_("""CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            title VARCHAR(80), note VARCHAR(500), author VARCHAR(40))""")
form = Form()
form.show()
app.exec_()
        
