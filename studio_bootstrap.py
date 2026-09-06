# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import hashlib


class MediareStudioBootstrap(gl.Contract):
    """Instancia de testes com layout v10.2 e upgrade restrito ao deployer."""
    case_id: str
    case_url: str
    status: str
    painel: str
    termo_opcao: str

    def __init__(self):
        self.case_id = ""
        self.case_url = ""
        self.status = "vazio"
        self.painel = ""
        self.termo_opcao = ""
        gl.storage.Root.get().upgraders.get().append(gl.message.sender_address)

    @gl.public.write
    def upgrade(self, new_code: bytes) -> None:
        root = gl.storage.Root.get()
        if gl.message.sender_address not in root.upgraders.get():
            raise gl.vm.UserError("UPGRADE_NAO_AUTORIZADO")
        if not new_code:
            raise gl.vm.UserError("CODIGO_VAZIO")
        code = root.code.get()
        code.truncate()
        code.extend(new_code)

    @gl.public.view
    def get_version(self) -> str:
        return "studio-bootstrap"

    @gl.public.view
    def get_code_hash(self) -> str:
        code = gl.storage.Root.get().code.get()
        return hashlib.sha256(code.slot().read(code.data_offset(), len(code))).hexdigest()

    @gl.public.view
    def can_upgrade(self) -> bool:
        return gl.message.sender_address in gl.storage.Root.get().upgraders.get()
