from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from petition.tasks import send_successful_petition_report


User = get_user_model()


def user_directory_path(instance, filename):
    return f"petition/{instance.owner.username}/{filename}"


class Petition(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petitions")
    recipient_name = models.CharField(max_length=100, default="Great Admin")
    recipient_email = models.EmailField(default="admin@admin.com")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=user_directory_path, default="default.jpg")
    slug = models.SlugField(max_length=50, unique=True, null=False, blank=True)
    goal = models.PositiveIntegerField(blank=False, null=False, default=10)
    is_successful = models.BooleanField(default=False)
    num_signatures = models.IntegerField(default=0)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Petition")
        verbose_name_plural = _("Petitions")

    def __str__(self):
        return f"{self.title} - {self.owner}"

    def get_summary(self):
        return self.description[:50]

    def get_relative_api_url(self):
        return reverse("petition:petition_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Petition, self).save(*args, **kwargs)



class Signature(models.Model):
    petition = models.ForeignKey(
        Petition, on_delete=models.CASCADE, related_name="signatures"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    let_me_know = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Signature")
        verbose_name_plural = _("Signatures")

    def __str__(self):
        return f"{self.petition} - {self.first_name} {self.last_name} - {self.email}"




class Reason(models.Model):
    petition = models.ForeignKey(
        Petition, on_delete=models.CASCADE, related_name="reasons"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    why = models.CharField(max_length=300)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Reason")
        verbose_name_plural = _("Reasons")

    def __str__(self):
        return f"{self.petition} - {self.why}"


class Vote(models.Model):
    class VoteChoice(models.TextChoices):
        like = "l", _("like")
        dislike = "d", _("dislike")

    reason = models.ForeignKey(Reason, on_delete=models.CASCADE, related_name="votes")
    vote = models.CharField(max_length=12, choices=VoteChoice.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")



@receiver(post_save, sender=Petition)
def mark_as_successful(sender, instance, **kwargs):
    if instance.num_signatures == instance.goal:
        Petition.objects.filter(id=instance.id).update(is_successful=True)
        p_obj = Petition.objects.get(id=instance.id)
        title = p_obj.title
        owner = f"{p_obj.owner.first_name} {p_obj.owner.last_name}"
        recipient_name = p_obj.recipient_name
        recipient_email = p_obj.recipient_email
        send_successful_petition_report.delay(title, owner, recipient_name, recipient_email)


@receiver(post_save, sender=Signature)
def update_signatures(sender, instance, **kwargs):
    if instance.is_verified is True:
        Petition.objects.filter(id=instance.petition.id).update(
            num_signatures=F("num_signatures") + 1
        )



@receiver(post_save, sender=Vote)
def update_votes(sender, instance, **kwargs):
    if instance.vote == Vote.VoteChoice.like:
        Reason.objects.filter(id=instance.reason.id).update(likes=F("likes") + 1)
    else:
        Reason.objects.filter(id=instance.reason.id).update(dislikes=F("dislikes") + 1)
