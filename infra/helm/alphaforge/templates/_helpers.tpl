{{- define "alphaforge.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "alphaforge.image" -}}
{{- printf "%s/%s:%s" .Values.global.image.registry .name (.tag | default .Values.global.image.tag) -}}
{{- end -}}

{{- define "alphaforge.labels" -}}
app.kubernetes.io/name: {{ .name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: alphaforge
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}
