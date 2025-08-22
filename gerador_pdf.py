# gerador_pdf.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch

from database import buscar_caso_por_id, buscar_atividades_por_caso_id

def gerar_pdf_relatorio(id_caso, caminho_salvar):
    """
    Gera um relatório completo em PDF para um caso específico.
    """
    try:
        # --- 1. Buscar os dados do banco de dados ---
        dados_caso = buscar_caso_por_id(id_caso)
        lista_atividades = buscar_atividades_por_caso_id(id_caso)

        if not dados_caso:
            print("Caso não encontrado para gerar PDF.")
            return False

        # --- 2. Configurar o documento e estilos ---
        doc = SimpleDocTemplate(caminho_salvar, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        style_titulo = ParagraphStyle(name='Titulo', parent=styles['h1'], alignment=TA_CENTER, fontSize=16)
        style_subtitulo = ParagraphStyle(name='Subtitulo', parent=styles['h2'], alignment=TA_CENTER, fontSize=14)
        style_corpo = ParagraphStyle(name='Corpo', parent=styles['Normal'], alignment=TA_JUSTIFY)
        
        story = [] # 'Story' é a lista de todos os elementos que irão no PDF

        # --- 3. Montar o conteúdo do PDF ---
        # Título principal e subtítulo
        story.append(Paragraph("DEPARTAMENTO DE AUDITORIA INTERNA", style_titulo))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"RELATÓRIO DE AUDITORIA - {dados_caso[1]}", style_subtitulo)) # dados_caso[1] é o título
        story.append(Spacer(1, 0.4*inch))

        # Parágrafo introdutório (exemplo)
        texto_intro = f"""
        Realizamos nos dias {dados_caso[4]} a {dados_caso[5] if dados_caso[5] else 'presente data'}, auditoria no {dados_caso[1]}, 
        onde analisamos os procedimentos adotados. Segue abaixo tabela contendo os testes realizados e situação encontrada:
        """
        story.append(Paragraph(texto_intro, style_corpo))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("RESUMO DOS TESTES REALIZADOS", styles['h3']))
        
        # --- 4. Montar a tabela de atividades ---
        dados_tabela = [["Nº", "Atividade", "Realizado Por", "Data"]] # Cabeçalhos
        for ativ in lista_atividades:
            # ativ[0] = id, ativ[1] = desc, ativ[2] = por, ativ[3] = data
            dados_tabela.append([ativ[0], Paragraph(ativ[1], styles['Normal']), ativ[2], ativ[3]])

        tabela = Table(dados_tabela, colWidths=[0.4*inch, 4*inch, 1.5*inch, 1*inch])
        
        # Estilo da tabela
        style_tabela = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#CCCCCC')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        tabela.setStyle(style_tabela)
        
        story.append(tabela)
        
        # --- 5. Gerar o PDF ---
        doc.build(story)
        print(f"PDF gerado com sucesso em: {caminho_salvar}")
        return True

    except Exception as e:
        print(f"Ocorreu um erro ao gerar o PDF: {e}")
        return False