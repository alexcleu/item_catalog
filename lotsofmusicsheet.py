from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Vocalband, Musicsheet

engine = create_engine('sqlite:///vocalbandmusic.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

vocalband1 = Vocalband(name="Awaken A Cappella", 
                       picture = "https://pbs.twimg.com/profile_images/378800000527416861/fe86b831877786cc54910cb083c65b0c_400x400.jpeg"
                       )

session.add(vocalband1)
session.commit()

Musicsheet1 = Musicsheet(name="I want you back", vocalband_id = 1, 
              vocal_part="SATB", vocalband=vocalband1, needs_beatbox=True)

session.add(Musicsheet1)
session.commit()

Musicsheet2 = Musicsheet(name="The Book of Love", vocalband_id = 1, 
              vocal_part="SATB", vocalband=vocalband1, needs_beatbox=True)

session.add(Musicsheet2)
session.commit()

Musicsheet3 = Musicsheet(name="Free Falling", vocalband_id = 1, 
              vocal_part="SATB", vocalband=vocalband1, needs_beatbox=True)

session.add(Musicsheet3)
session.commit()

Musicsheet4 = Musicsheet(name="Forget You", vocalband_id = 1, 
              vocal_part="SATB", vocalband=vocalband1, needs_beatbox=True)

session.add(Musicsheet4)
session.commit()


vocalband2 = Vocalband(name="Scattertones",
                       picture="https://yt3.ggpht.com/--6gAmZzfPIU/AAAAAAAAAAI/AAAAAAAAAAA/aDVxxQZcThI/s900-c-k-no/photo.jpg"
                       )

session.add(vocalband2)
session.commit()

Musicsheet1 = Musicsheet(name="Paradise", vocalband_id = 2, 
              vocal_part="SATB", vocalband=vocalband2, needs_beatbox=True)

session.add(Musicsheet1)
session.commit()

Musicsheet2 = Musicsheet(name="No Women No Cry", vocalband_id = 2, 
              vocal_part="SATB", vocalband=vocalband2, needs_beatbox=True)

session.add(Musicsheet2)
session.commit()

Musicsheet3 = Musicsheet(name="Thinking About You", vocalband_id = 2, 
              vocal_part="SATB", vocalband=vocalband2, needs_beatbox=True)

session.add(Musicsheet3)
session.commit()

Musicsheet4 = Musicsheet(name="Stop this Train", vocalband_id = 2, 
              vocal_part="SATB", vocalband=vocalband2, needs_beatbox=True)

session.add(Musicsheet4)
session.commit()

vocalband3 = Vocalband(name="Bruin Harmony",
                       picture="http://static1.squarespace.com/static/5410fd61e4b07bc380c46d7c/t/541b30e7e4b09a2902b5ec35/1444522695501/?format=1500w"
                       )

session.add(vocalband3)
session.commit()

Musicsheet1 = Musicsheet(name="Madness", vocalband_id = 3, 
              vocal_part="SATB", vocalband=vocalband3, needs_beatbox=True)

session.add(Musicsheet1)
session.commit()

Musicsheet2 = Musicsheet(name="Hold it against me", vocalband_id = 3, 
              vocal_part="SATB", vocalband=vocalband3, needs_beatbox=True)

session.add(Musicsheet2)
session.commit()

Musicsheet3 = Musicsheet(name="Somebody's Baby", vocalband_id = 3, 
              vocal_part="SATB", vocalband=vocalband3, needs_beatbox=True)

session.add(Musicsheet3)
session.commit()

Musicsheet4 = Musicsheet(name="Ignition Remix", vocalband_id = 3, 
              vocal_part="SATB", vocalband=vocalband3, needs_beatbox=True)

session.add(Musicsheet4)
session.commit()




