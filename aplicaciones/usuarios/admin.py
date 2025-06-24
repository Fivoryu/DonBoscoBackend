from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, Notificacion, Bitacora, SuperAdmin, Admin, Puesto, Accion, ModeloPermitido, PermisoPuesto, PermisoRol

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nombre', 'apellido', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'nombre', 'apellido', 'ci')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('ci', 'nombre', 'apellido', 'email', 'foto', 'telefono')  # 'edad' removed
        }),
        ('Roles y Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'ci', 'email', 'nombre', 'apellido', 'password1', 'password2', 'rol'),
        }),
    )

class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'fecha', 'leida', 'tipo')
    list_filter = ('leida', 'tipo')
    search_fields = ('titulo', 'mensaje', 'usuario__username')
    date_hierarchy = 'fecha'

class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'hora_entrada', 'hora_salida', 'duracion')
    list_filter = ('usuario__rol',)
    search_fields = ('usuario__username',)
    date_hierarchy = 'hora_entrada'
    
    def duracion(self, obj):
        if obj.hora_salida:
            return obj.hora_salida - obj.hora_entrada
        return "Sesión activa"
    duracion.short_description = 'Duración'

class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario__username', 'usuario__email')

class AdminAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puesto', 'estado')
    list_filter = ('estado', 'puesto')
    search_fields = ('usuario__username', 'puesto')

class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

class AccionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class ModeloPermitidoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class PermisoPuestoAdmin(admin.ModelAdmin):
    list_display = ('puesto', 'modelo', 'accion')
    list_filter = ('puesto', 'modelo', 'accion')
    search_fields = ('puesto__nombre', 'modelo__nombre', 'accion__nombre')

@admin.register(PermisoRol)
class PermisoRolAdmin(admin.ModelAdmin):
    list_display  = ('rol', 'modelo', 'accion')
    list_filter   = ('rol', 'modelo', 'accion')
    search_fields = ('rol__nombre', 'modelo__nombre', 'accion__nombre')



# Elimina cualquier registro duplicado de modelos en admin.site.register
# Si tienes admin.site.register(Puesto) en models.py, elimínalo de allí.
# Solo registra aquí en admin.py:

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(Notificacion, NotificacionAdmin)
admin.site.register(Bitacora, BitacoraAdmin)
admin.site.register(SuperAdmin, SuperAdminAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Puesto, PuestoAdmin)
admin.site.register(Accion, AccionAdmin)
admin.site.register(ModeloPermitido, ModeloPermitidoAdmin)
admin.site.register(PermisoPuesto, PermisoPuestoAdmin)