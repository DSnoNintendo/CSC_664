import app
from app.backend.utils import randomize_mtime, gallery_as_path_list
from app.frontend.components import GalleryImage

program = app.start()
program.mainloop()


