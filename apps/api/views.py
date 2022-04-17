from rest_framework.generics import RetrieveAPIView

from .serializers import GradesSerializers
from mainapp.models import Grade


class GradesDetailView(RetrieveAPIView):
    serializer_class = GradesSerializers
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            school = self.request.user.school
            user_type = self.request.user.user_type
            match user_type:
                case "T":
                    return Grade.objects.filter(
                        exam__exam_class__subjects__teacher__user=self.request.user)
                case "SS":
                    return Grade.objects.filter(exam__exam_class__school=school)
                case "S":
                    return Grade.objects.filter(student__user=self.request.user)
        return Grade.objects.none()