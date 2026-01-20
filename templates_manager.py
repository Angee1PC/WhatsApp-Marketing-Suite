class TemplateManager:
    @staticmethod
    def get_suggestions(category):
        if category == "Ventas (Producto/Inmueble)":
            return [
                "Hola {Nombre}! 👋 Espero estés teniendo excelente día. Vi que solicitaste información sobre nuestros productos. ¿Sigues buscando opciones?",
                "¡Hola {Nombre}! 🏠 Soy tu asesor digital. Tenemos nuevas ubicaciones disponibles que coinciden con tu búsqueda. ¿Te gustaría ver las fotos?",
                "Saludos {Nombre}. 🌟 Solo para comentarte que tenemos una promoción especial válida solo por esta semana. ¿Te envío los detalles?",
                "Hola {Nombre}, un gusto saludarte. 👋 ¿Pudiste revisar la información que enviamos anteriormente? Quedo atento a tus dudas.",
                "¡Hola {Nombre}! ✨ Vimos que visitaste nuestra página. Si tienes alguna pregunta específica sobre precios o modelos, estoy aquí para ayudarte.",
                "Buen día {Nombre}! 📦 Te escribo para ver si ya estás listo para realizar tu pedido o si necesitas más especificaciones técnicas.",
                "Hola {Nombre}. 👋 Tenemos inventario limitado de lo que buscabas. Si te interesa apartar, avísame con un mensaje.",
                "¡Hola {Nombre}! 🚀 Acabamos de lanzar un nuevo producto y pensé en ti. ¿Te gustaría ser de los primeros en conocerlo?",
                "Estimado {Nombre}, ¿cómo va tu proceso de compra? Recuerda que podemos ofrecerte facilidades de pago si te animas hoy. 💳",
                "Hola {Nombre}! 👋 Solo un breve recordatorio de que sigo a tu disposición para cualquier consulta. ¡Bonito día!"
            ]
        elif category == "Citas (Reservar/Confirmar)":
            return [
                "Hola {Nombre}, confirmamos tu cita para mañana. 🗓️ ¿Podrías confirmar asistencia respondiendo 'SÍ'?",
                "Saludos {Nombre}. 🕒 Te recuerdo que es momento de agendar tu mantenimiento/visita periódica. ¿Qué día te queda mejor?",
                "Hola {Nombre}! 👋 Soy del equipo de soporte/atención. Para asegurar tu espacio en la agenda, por favor confirma tu asistencia.",
                "¡Hola {Nombre}! Notamos que hace tiempo no nos visitas. ¿Te gustaría reactivar tus sesiones con un descuento especial? 📅",
                "Estimado {Nombre}, necesitamos reconfirmar tu horario de visita para mañana. ¿Sigues disponible en la hora acordada?",
                "Hola {Nombre}, espero estés bien. 🦷/🩺 ¿Te gustaría aprovechar algún espacio libre esta semana para tu chequeo?",
                "¡Hola {Nombre}! 👋 Estamos organizando la agenda de la próxima semana. ¿Te apartamos un lugar el martes o jueves?",
                "Saludos {Nombre}. Tu servicio está próximo a vencer. ¿Te gustaría renovarlo hoy mismo para no perder cobertura? 🛡️",
                "Hola {Nombre}, un favor. 🙏 ¿Podrías confirmarme si asistirás a la reunión programada? Responde SÍ o Reprogramar.",
                "¡Hola {Nombre}! ✨ Tenemos nuevos horarios extendidos para mejor atención. Si quieres cambiar tu cita a la tarde, avísame."
            ]
        return []
