from audioop import reverse
import io
import os
from PIL import Image as im
from django.http import HttpResponseRedirect
import torch


from django.shortcuts import render
from django.views.generic.edit import CreateView

from .models import ImageModel
from .forms import ImageUploadForm


class UploadImage(CreateView):
    model = ImageModel
    template_name = 'image/imagemodel_form.html'
    fields = ["image"]

    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES.get('image')
            img_instance = ImageModel(
                image=img
            )
            img_instance.save()

            uploaded_img_qs = ImageModel.objects.filter().last()

            img_bytes = uploaded_img_qs.image.read()
            img = im.open(io.BytesIO(img_bytes))

            model = torch.hub.load(r'/home/ram/Py_Prac_WSL/django_yolo_api/yolov5_code', 'custom',
                                   path=r'/home/ram/Py_Prac_WSL/django_yolo_api/yolov5_code/weights/yolov5s.pt', source='local')

            results = model(img, size=640)
            results.render()
            for img in results.imgs:
                img_base64 = im.fromarray(img)
                img_base64.save("media/yolo_out/image0.jpg", format="JPEG")

            inference_img = "/media/yolo_out/image0.jpg"

            form = ImageUploadForm()
            context = {
                "form": form,
                "inference_img": inference_img
            }
            return render(request, 'image/imagemodel_form.html', context)

        else:
            form = ImageUploadForm()

        context = {
            "form": form
        }

        return render(request, 'image/imagemodel_form.html', context)
