from verificacion import enviar_codigo_desde_gmail, generar_codigo_temporal

correo_prueba = "tu_correo_institucional@bbva.com"
codigo = generar_codigo_temporal()
resultado = enviar_codigo_desde_gmail(correo_prueba, codigo)

print("✅ Enviado" if resultado else "❌ Falló el envío")
