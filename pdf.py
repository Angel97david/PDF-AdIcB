import flet as ft
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import fitz 
import io
from PIL import Image
import base64
import os
from pikepdf import Pdf


def encryption(password,path):
    reader = PdfReader(path)
    writer = PdfWriter()

    if not reader.is_encrypted: 
        try:
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            with open(path, "wb") as f:
                writer.write(f)
            os.startfile(path)

            return 'Tu PDF ahora está protegido'
        except:
            return 'Algo salio mal intenta de nuevo'
    else:
        return 'Error ya tiene una contraseña '
           
def dencryption(password,path):
    reader = PdfReader(path)
    writer = PdfWriter()
    
    if reader.is_encrypted: 
        try:
            reader.decrypt(password)

            for page in reader.pages:
                writer.add_page(page)
        
            with open(path, "wb") as f:
                writer.write(f)    
            os.startfile(path)
            return 'Tu PDF ya no tiene contraseña' 
        except:
           return 'La contraseña es incorrecta, intenta de nuevo '
    else:
        return 'Tu PDF no tiene contraseña' 

def save_PDF(funcion,page,merger):
        selector_Save = ft.FilePicker(lambda e: funcion(e,merger))
        page.overlay.append(selector_Save)
        
        add = lambda: selector_Save.save_file(
            dialog_title="Guardar PDF como...",
            file_name="nuevo.pdf",
            allowed_extensions=["pdf"]
        )
        page.update()
        add()

def combine_PDF(e:ft.FilePickerResultEvent, page,col_imagenes,name_PDF):
    
    try:  
        
        def join_PDF_Save(e:ft.FilePickerResultEvent,merger):   
            
            try:
                path = Path(e.path)
                if path.suffix.lower() != '.pdf':
                   path = path.with_suffix('.pdf') 
                merger.write(path)
                
                merger.close()  
                os.startfile(path) 
                message_Alert('La combinación de los archivos PDF se realizó con éxito.',page)  
                view_PDF_Combine_Image(col_imagenes,page,path,path.name)      
                
            except:
               message_Alert('Cerro la ventana, intente nuevamente',page) 
                
        name_PDF.value = f"Selecciono {len(e.files) } archivos"
        name_PDF.color= ft.Colors.BLACK
        merger = PdfWriter()                  
        
        for i in e.files:
            reader = PdfReader(i.path)
            if reader.is_encrypted:
                message_Alert(f'El archivo PDF {i.name} está protegido con contraseña. Elimine la contraseña e inténtelo nuevamente.  ',page)
                merger= PdfWriter()
                break
            else:
                merger.append(i.path)
        if len(merger.pages) > 0:
            save_PDF(join_PDF_Save,page,merger)
            
        page.update()      
               
    except:
       message_Alert('Algo salio mal intenta de nuevo',page) 


def delete_or_Extract_Pages_PDF(e: ft.FilePickerResultEvent,pag,page,option):
    try:
        pages = pag.value.split(",")
        path = ''
        if pages[-1] == '':
            pages.pop()
        
        if not e.files:
            pass
        elif len(pages) == 0:    
            message = 'eliminar' if option == 1 else 'Extraer'
            message_Alert(f'Ingrese primero el número(s) de las página(s) que quiere {message} ',page) 
            
        elif len(pages) >= 1:
            state = False
            for x in e.files:
                dst = Pdf.new()
                path = x.path
                path_Original = Path(path)
                pdf = Pdf.open(path)

                for n, p in enumerate(pdf.pages):  
                    for i in range(0, len(pages)):
                        if int(pages[i]) > len(pdf.pages):
                            state = True
                            break
                        elif option == 1 and n != int(pages[i])-1:
                            dst.pages.append(p)
                        elif option == 2 and n == int(pages[i])-1:
                            dst.pages.append(p)    
               
                if state == True:
                    message_Alert(f'la página(s) ingresadas no existen' ,page)  
                elif path_Original.exists() and len(pages) == len(pdf.pages):
                    message_Alert('Las páginas seleccionadas son las mismas que tiene el PDF' ,page)
                elif path_Original.exists():
                    name_PDF_New = 'Eliminado' if option == 1 else 'Nuevo'
                    Path_New = f'{path_Original.with_name(f'{name_PDF_New}{path_Original.name}')}'
                    
                    def new_Name(name_Path,cont):
                        name_Path = Path(name_Path)
                        if name_Path.exists():
                            cont += 1
                            name_Path = name_Path.with_name(f'{name_Path.stem}({cont}){name_Path.suffix}')
                            
                            new_Name(name_Path,cont)
                        else:
                            dst.save(name_Path)
                            message = 'eliminaron' if option == 1 else 'Extrageron'
                            os.startfile(name_Path)
                            message_Alert(f'Paginas {pag.value} se {message}, y se guardo con el nombre nuevo{name_Path.name} ',page) 
                    cont = 0
                    new_Name(Path_New,cont) 
    except:
       message_Alert('Algo salio mal, verifique que los archivos no tengan contraseña, los valores ingresados sean correctos ' ,page)
  
    
def message_Alert(message, page):  
    def close(dlg):
            page.close(dlg)  
    
    dlg = ft.AlertDialog(       
        title=ft.Text("Notificación", text_align=ft.TextAlign.CENTER,weight=ft.FontWeight.BOLD),
        content=ft.Text(f"{message}", text_align=ft.TextAlign.CENTER,size=20),
        alignment=ft.alignment.center,
        title_padding=ft.padding.all(5),
        actions =
        [
            ft.Container(
                content = ft.Column(
                    controls = [
                        ft.ElevatedButton(
                            text = "Cerrar",
                            #on_click=lambda e: page.close(dlg),
                            on_click= lambda e: close(dlg),
                            color=ft.Colors.WHITE,
                            bgcolor= ft.Colors.BLACK,
                            style= ft.ButtonStyle(
                                text_style=ft.TextStyle(
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            expand=True,
                            width=150,
                            height=40,                  
                        )
                    ],
                    alignment= ft.MainAxisAlignment.CENTER,
                    horizontal_alignment= ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
            ) 
        ]
    )
    
    page.open(dlg)
    dlg.open = True
    page.update()        

def pdf_page_to_image(pdf_path, page_number=0):
    """Convierte una página del PDF a una imagen PNG en memoria."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  
    img_data = io.BytesIO(pix.tobytes("png"))
    return img_data
 
def image_PDF(image_data,name):
    image = ft.Image(src_base64=base64.b64encode(image_data.getvalue()).decode(),
        width=200,
        height=100,
        fit=ft.ImageFit.CONTAIN
    )
    
    return  ft.Container(
        content = ft.Column(
            controls=
            [
                image,ft.Text(f'{name}',size=25,no_wrap=False,max_lines = 1,
                                    text_align=ft.TextAlign.CENTER, italic=True
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        border= ft.border.all(1, ft.Colors.BLACK),
        border_radius=15,
        width= 230,
        height= 200,
        bgcolor= "#61C0F0",
        alignment= ft.alignment.center,
    )     
     
def view_PDF_Combine_Image(col_imagenes,page,path,name):
    
    col_imagenes.controls.clear(),
    col_imagenes.controls.append(
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        image_PDF(pdf_page_to_image(path),name),            
                                    ],
                                )
                            ],
                        ),    
                    ),
    page.update()    

def metadata(e:ft.FilePickerResultEvent,page,list_Metadata):
    try:
        reader = PdfReader(e.files[0].path)
        meta = reader.metadata

        list_Metadata['author'].value = f'Author: {meta.author}' if meta.author else 'Author: No disponible'
        list_Metadata['creator'].value = f'Creador: {meta.creator}' if meta.creator else 'Creador: No disponible'
        list_Metadata['producer'].value = f'Productor: {meta.producer}' if meta.producer else 'Productor: No disponible'
        list_Metadata['subject'].value = f'Asunto: {meta.subject}' if meta.subject else 'Asunto: No disponible'
        list_Metadata['title'].value = f'Titulo: {meta.title}' if meta.title else 'Titulo: No disponible'
        page.update()
    except:
        message_Alert('Este docuemnto no tiene disponible los metadatos',page)    
      
def select_file(e: ft.FilePickerResultEvent,name_PDF, password, action, page): 
    pdf= []
    try:
        if password.value and action != 2:
            if e.files:
                if len(e.files) >= 2:
                    name_PDF.value = f"Selecciono {len(e.files) } archivos"
                    name_PDF.color= ft.Colors.BLACK
                else:
                    file = e.files[0]
                    name_PDF.value = f"Seleccionaste: {file.name}"
                    name_PDF.color= ft.Colors.BLACK
                    
                for i in e.files:
                    if action == 1:
                        respon = encryption(password.value,i.path)    
                    elif action == 0:
                        respon = dencryption(password.value,i.path)   
                message_Alert(respon,page)
            else:
                name_PDF.value = "No se seleccionó ningún archivo"
              
        elif not password.value :
            message_Alert('Primero ingrese una contraseña',page)
        page.update()
        
    except :
       message_Alert('¡Algo salió mal! Verifique que los PDF no tengan contraseña ni estén corruptos.',page)    

def main(page: ft.Page):
    
    page.title = "AdicB"
    page.window.icon = '../Image/logo.png'
    page.window.width = 1200
    page.window.height = 800
    page.window.resizable = False
    page.bgcolor= '#bccad2'
    page.window.center()
            
    title = ft.Container( alignment=ft.alignment.center ,content = ft.Text("Bienvenidos a PDF AdIcB", size=30, italic=True, text_align=ft.TextAlign.CENTER,weight=ft.FontWeight.BOLD)
    )
    
    description = ft.Text('''Este programa permite agregar o eliminar contraseñas a archivos PDF de manera sencilla y segura. Asimismo, ofrece la opción de unir varios documentos PDF o dividirlos según sus necesidades.'''
                    , italic=True , no_wrap=False, text_align=ft.TextAlign.JUSTIFY,size=20 )
    
    name_PDF = ft.Text("Ningún archivo seleccionado",width=400, size=18,weight=ft.FontWeight.W_700,color=ft.Colors.RED,italic=True,)
    
    password  = ft.TextField(label='Escribe contraseña del PDF',expand= True)
    
    number_PDFs_Delete  = ft.TextField(label='Escriba el número de páginas.',expand= 5)
    
    number_PDFs_Extract  = ft.TextField(label='Escriba el número de páginas.',expand= 5)
   
    list_Metadata = {
        "author" : ft.Text("Author: "),
        "creator" :ft.Text("Creador: "),
       "producer" : ft.Text("Productor: "),
        "subject": ft.Text("Asunto: "),
        "title": ft.Text("Titulo: "),
    }    
    
    # Create of the FilePicker,To add a password, we send 1 and to remove a password, we send 0, we send 2 to open files
    selector_Remove = ft.FilePicker(on_result = lambda e: select_file(e,name_PDF,password,0, page))
    page.overlay.append(selector_Remove)
    
    selector_Add = ft.FilePicker(on_result = lambda e: select_file(e,name_PDF,password,1, page))
    page.overlay.append(selector_Add)

    #combine_PDF(pdfs,page,col_imagenes)
    selector_open = ft.FilePicker(on_result = lambda e: combine_PDF(e,page,col_imagenes,name_PDF))
    page.overlay.append(selector_open) 
    
    # option 1 if delete pages of PD, we send 2 if extract PDF
    selector_Delete_PDF = ft.FilePicker(on_result = lambda e: delete_or_Extract_Pages_PDF(e,number_PDFs_Delete,page,1))
    page.overlay.append(selector_Delete_PDF)
    
    selector_Extract_PDf = ft.FilePicker(on_result = lambda e: delete_or_Extract_Pages_PDF(e,number_PDFs_Extract,page,2))
    page.overlay.append(selector_Extract_PDf)
    
    selector_MetaData = ft.FilePicker(on_result = lambda e: metadata(e,page,list_Metadata))
    page.overlay.append(selector_MetaData)
    
    #add password to PDF 
    add_password = ft.ElevatedButton(
        text="Agregar Contraseña al PDF",
        on_click=lambda _: selector_Add.pick_files(
            allow_multiple=True, 
            allowed_extensions=["pdf"]  
        ),
        color=ft.Colors.WHITE,
        bgcolor= ft.Colors.BLACK,
        expand=5,
        height=40,
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(
                size=15,
                weight=ft.FontWeight.BOLD
            )
        )
    )

    #Remove password to PDF 
    remove_password = ft.ElevatedButton(
        text='Quitar contraseña al PDF',
        on_click=lambda _: selector_Remove.pick_files(
            allow_multiple=True, 
            allowed_extensions=["pdf"]  
        ),
         color=ft.Colors.WHITE,
        bgcolor= ft.Colors.BLACK,
        expand=5,
        height=40,
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(
                size=15,
                weight=ft.FontWeight.BOLD
            )
        )
    )
    
    #Button open de PDFs for combine  
    open_PDF = ft.ElevatedButton(
        text = 'Combinar PDFs',
        on_click=lambda _: selector_open.pick_files(
            dialog_title= 'Seleccione los archivos para combinar',
            allow_multiple=True,
            allowed_extensions=['pdf']
        ),
        bgcolor= ft.Colors.BLACK,
        color= ft.Colors.WHITE,
        height= 40,
        expand= 5,
        style= ft.ButtonStyle(
            text_style= ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15,
            ),
            alignment=ft.alignment.center
        )
    )
    #Button open pdf for delete pages
    delete_Page_PDF = ft.ElevatedButton(
        text = 'Eliminar páginas del pdf',
        on_click=lambda _: selector_Delete_PDF.pick_files(
            dialog_title= 'Seleccione el archivo(s) para eliminar la(s) pagina(s) ',
            allow_multiple=True,
            allowed_extensions=['pdf']
        ),
        bgcolor= ft.Colors.BLACK,
        color= ft.Colors.WHITE,
        height= 40,
        expand= 5,
        style= ft.ButtonStyle(
            text_style= ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15
            )
        )
    )
    
    #Button open pdf for extract pages
    Extract_Page_PDf = ft.ElevatedButton(
        text = 'Extraer página(s) del PDFs',
        on_click=lambda _: selector_Extract_PDf.pick_files(
            dialog_title= 'Seleccione el archivos para extraer la(s) pagina(s) ',
            allow_multiple=True,
            allowed_extensions=['pdf']
        ),
        bgcolor= ft.Colors.BLACK,
        color= ft.Colors.WHITE,
        height= 40,
        expand= 5,
        style= ft.ButtonStyle(
            text_style= ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15
            )
        )
    )
    
    #Button extract metadata
    Metadata_PDF = ft.ElevatedButton(
        text = 'Extraer metadatos PDFs',
        on_click=lambda _: selector_MetaData.pick_files(
            dialog_title= 'Seleccione el archivos para extraer Metadatas ',
            allow_multiple=False,
            allowed_extensions=['pdf']
        ),
        bgcolor= ft.Colors.BLACK,
        color= ft.Colors.WHITE,
        expand= True,
        height= 40,
        style= ft.ButtonStyle(
            text_style= ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=15
            )
        )
    )
    note_Encryte_Desencryte = ft.Text(
        ' Para agregar o quitar la contraseña de un documento PDF: \n 1. Ingrese la contraseña en el campo de texto ubicado abajo.\n  2. Luego haga clic en el botón correspondiente: Agregar contraseña o Eliminar contraseña.  ',
        color= ft.Colors.RED,
        size= 15,
        italic=True,
        text_align= ft.TextAlign.CENTER,
        expand= True
    )
    
    note_Combine = ft.Text(
        ' Una vez seleccionados los archivos, se mostrará el archivo combinado. ',
        color= ft.Colors.RED,
        size= 15,
        italic=True,
        text_align= ft.TextAlign.CENTER,
        expand= 5
    )
    
    note_Delete = ft.Text(
        'Escriba los números de las páginas que desea eliminar del PDF, separados por comas. Ejemplo: 1, 2, 3 — se eliminarán esas páginas, en un nuevo archivo con nombre Eliminado+nombre del pdf original.',
        color= ft.Colors.RED,
        size= 15,
        italic=True,
        text_align= ft.TextAlign.CENTER,
        expand= True
    )
    
    note_Extract = ft.Text(
        'Escriba los números de las páginas que desea extraer del PDF, separados por comas. Ejemplo: 1, 2, 3 — se extraerán esas páginas, en un nuevo archivo con nombre nuevo+nombre del pdf original.',
        color= ft.Colors.RED,
        size= 15,
        italic=True,
        text_align= ft.TextAlign.CENTER,
        expand= True
    )
    
    col_imagenes = ft.Row(
        controls=[
            ft.Row(
               controls = [
                    ft.Image(
                        src=f'../Image/PDF.png',
                        width= 400,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    )   
                ],
               wrap=True,
               expand=True,
               alignment=ft.MainAxisAlignment.CENTER,
               spacing = 0,
            )
        ],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True
    )
       
    
    join_PDF = ft.Container(
        content = col_imagenes,
        expand = True,
        alignment = ft.alignment.center,
        border_radius= 10,
        height=210,
    )
        
    container_Left = ft.Container(
        content = ft.Column(
            [
                note_Encryte_Desencryte,
                ft.Column(
                    [
                        name_PDF,
                        password,
                        
                    ]
                ),
                
                ft.Row(
                    [
                        remove_password,
                        add_password,
                    ]
                ),
                
                ft.Column(
                    controls = [
                                                
                        ft.Row(
                            controls=
                                [   
                                    open_PDF,
                                    note_Combine, 
                                ],    
                            alignment=ft.MainAxisAlignment.CENTER,  
                        ),
                        
                        join_PDF,

                    ],  
                )
            ],
                alignment= ft.alignment.center,
        ),
        padding= ft.padding.all(30),
        margin=ft.margin.only( right = 15 ),
        expand=5,
        height = 600,
        border_radius=  20,
        bgcolor= "#d9e0e5"
    )
    
    container_Right = ft.Container(
        content = 
            ft.Column(
                controls = [
                    note_Extract,
                    ft.Row(
                        controls= [
                            Extract_Page_PDf,
                            number_PDFs_Extract
                        ]
                    ),
                    
                    list_Metadata['author'],
                    list_Metadata['creator'],
                    list_Metadata['producer'],
                    list_Metadata['subject'],
                    list_Metadata['title'],
                    
                    ft.Row(
                       controls=[
                           Metadata_PDF,
                       ]
                    ),
                    
                    note_Delete,
                    ft.Row(
                        controls=
                            [   
                                number_PDFs_Delete,
                                delete_Page_PDF,
                            ],      
                    ),
                ],
                expand = True
            ),
        expand=5,
        height = 600,
        border_radius=  20,
        margin=ft.margin.only( left = 15 ),
        padding= ft.padding.all(30),
        bgcolor= "#d9e0e5"
    )
    
    container_Main= ft.Container(
        content = ft.Column(
            controls=[
                title,
                description,
                
                ft.Row(
                controls = [
                        container_Left,
                        container_Right
                    ],
                    spacing=0
                )
            ],
            scroll=ft.ScrollMode.ALWAYS,
            
        ),
        expand=True,
        margin= ft.margin.all(30),
        padding=ft.padding.all(0),
    )
    page.add(container_Main)
    
ft.app(target=main)

