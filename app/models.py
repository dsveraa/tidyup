from sqlalchemy import Column, Index, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from . import db

class Actividad(db.Model):
    __tablename__ = 'actividades'
    
    id = Column(Integer, primary_key=True)
    actividad = Column(String)

class Tarea(db.Model):
    __tablename__ = 'tareas'

    id = Column(Integer, primary_key=True)
    tarea = Column(String)

class Responsable(db.Model):
    __tablename__ = 'responsables'
    
    id = Column(Integer, primary_key=True)
    responsable = Column(String, unique=True)

class Dias(db.Model):
    __tablename__ = 'dias'
    
    id = Column(Integer, primary_key=True)
    dia = Column(Enum('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo', name='dias_enum'), nullable=False)

class Agenda(db.Model):
    __tablename__ = 'agenda'
    
    id = Column(Integer, primary_key=True)
    responsable_id = Column(Integer, ForeignKey('responsables.id'))
    actividad_id = Column(Integer, ForeignKey('actividades.id'))
    dia_id = Column(Integer, ForeignKey('dias.id'))
    completado = Column(Boolean, default=False)
    
    __table_args__ = (UniqueConstraint('responsable_id', 'actividad_id', 'dia_id', name='unique_agenda_entry'),)
    Index('idx_responsable_actividad_dia', 'responsable_id', 'actividad_id', 'dia_id')

class DetalleActividad(db.Model):
    __tablename__ = 'detalle_actividades'
    
    id = Column(Integer, primary_key=True)
    actividad_id = Column(Integer, ForeignKey('actividades.id'))
    tarea_id = Column(Integer, ForeignKey('tareas.id'))
