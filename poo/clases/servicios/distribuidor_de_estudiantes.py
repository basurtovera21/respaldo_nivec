#Paralelo
class DistribuidorDeEstudiantes:
    def __init__(self, lista_paralelos):
        self.paralelos = lista_paralelos

    def distribuir(self, lista_estudiantes):
        estudiantes_no_asignados = []
        for estudiante in lista_estudiantes:
            mejor_paralelo = self._encontrar_mejor_paralelo()
            if mejor_paralelo:
                mejor_paralelo.vincular_estudiante(estudiante)
            else:
                estudiantes_no_asignados.append(estudiante)
        return estudiantes_no_asignados

    def _encontrar_mejor_paralelo(self):
        paralelos_con_cupo = [p for p in self.paralelos if p.tiene_cupo_disponible()]
        if not paralelos_con_cupo:
            return None
        return min(paralelos_con_cupo, key=lambda p: len(p._estudiantes_matriculados))
