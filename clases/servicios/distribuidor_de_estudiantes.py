#Paralelo
class DistribuidorDeEstudiantes:
    def __init__(self, lista_paralelos):
        self.paralelos = lista_paralelos


    def distribuir(self, lista_estudiantes):
        estudiantes_no_asignados = []
        for estudiante in lista_estudiantes:
            mejor_paralelo = self._encontrar_mejor_paralelo(estudiante)
            if mejor_paralelo:
                mejor_paralelo.vincular_estudiante(estudiante)
                
            else:
                estudiantes_no_asignados.append(estudiante)

        return estudiantes_no_asignados


    def _encontrar_mejor_paralelo(self, estudiante):
        paralelos_compatibles = []
        for paralelo in self.paralelos:
            es_compatible = (paralelo.jornada == estudiante.jornada and paralelo.carrera == estudiante.carrera)
            if es_compatible and paralelo.tiene_cupo_disponible():
                paralelos_compatibles.append(paralelo)

        if not paralelos_compatibles:
            return None

        paralelo_con_menos_carga = paralelos_compatibles[0]
        for paralelo in paralelos_compatibles:
            if len(paralelo._estudiantes_matriculados) < len(paralelo_con_menos_carga._estudiantes_matriculados):
                paralelo_con_menos_carga = paralelo

        return paralelo_con_menos_carga