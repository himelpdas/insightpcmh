if not request.extension.lower() == 'pdf':
    redirect(URL(f=request.function + ".pdf", args=request.args, vars=request.get_vars))


def index():
    response.title = ""
    return DOC_HEADER()

def same_day_block_practice_fusion():

    response.title = ""