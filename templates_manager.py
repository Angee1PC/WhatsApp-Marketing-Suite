class TemplateManager:
    @staticmethod
    def get_suggestions(category):
        if category == "Ventas (Producto/Inmueble)":
            return [
                "Hola {Nombre}! 👋 Vi que te interesaste en nuestro producto. ¿Te gustaría ver el catálogo actualizado? 📦",
                "¡Hola {Nombre}! Soy tu asistente virtual. 🤖 Tenemos una oferta especial hoy en lo que buscas. ¿Te mando info?",
                "Saludos {Nombre}, espero estés bien. Estoy actualizando nuestra lista de interesados. ¿Sigues buscando comprar? 🏠",
                "Hola {Nombre}! 👋 Solo paso para recordarte que nos quedan pocas unidades de tu interés. ¡Avísame si quieres apartar!",
                "¡Hola {Nombre}! ✨ Vimos tu perfil y creemos que esta nueva colección te va a encantar. ¿Le echas un ojo? 👀"
            ]
        elif category == "Citas (Reservar/Confirmar)":
            return [
                "Hola {Nombre}, confirmamos tu cita para mañana. 🗓️ ¿Podrías confirmar con un 'SÍ'?",
                "Saludos {Nombre}. 🕒 Te recuerdo que tenemos un espacio disponible esta semana. ¿Te gustaría agendar?",
                "Hola {Nombre}! 👋 Soy del consultorio/oficina. Para confirmar tu asistencia, por favor responde este mensaje.",
                "¡Hola {Nombre}! Notamos que hace tiempo no vienes. ¿Te gustaría reservar una nueva sesión? 📅",
                "Estimado {Nombre}, necesitamos reconfirmar tu horario de visita. ¿Sigues disponible? Responde SÍ o NO."
            ]
        return []
