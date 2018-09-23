from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch.dispatcher import receiver
from mutagen.mp3 import MP3


class Album(models.Model):
    name = models.CharField(max_length=90)
    image = models.ImageField(upload_to='documents/images',
                              null=True,
                              blank=True)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Artist(models.Model):
    alias = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.alias:
            return self.alias
        return self.first_name


class Track(models.Model):
    file = models.FileField(upload_to='documents/music')
    name = models.CharField(max_length=30)
    duration = models.PositiveSmallIntegerField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    album = models.ForeignKey(Album,
                              on_delete=models.CASCADE,
                              related_name='tracks',
                              blank=True,
                              null=True)
    artists = models.ManyToManyField(Artist,
                                     related_name='tracks',
                                     through='TrackArtist',
                                     through_fields=('track',
                                                     'artist'))
    genders = models.ManyToManyField(Gender,
                                     related_name='tracks',
                                     through='TrackGender',
                                     through_fields=('track',
                                                     'gender'))

    def __str__(self):
        return self.name


class TrackArtist(models.Model):
    track = models.ForeignKey(Track,
                              on_delete=models.CASCADE)
    artist =  models.ForeignKey(Artist,
                                on_delete=models.CASCADE)

    def __str__(self):
        return '{0} : {1}'.format(self.track.name,
                                  self.artist.alias)

    class Meta:
        unique_together = ('track', 'artist')


class TrackGender(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} : {1}'.format(self.track.name,
                                  self.gender.name)


    class Meta:
        unique_together = ('track', 'gender')


class PlayList(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='playlists')
    tracks = models.ManyToManyField(Track,
                                    through='PlayListTrack',
                                    through_fields=('playlist',
                                                    'track'))

    def __str__(self):
        return self.name


class PlayListTrack(models.Model):
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} : {1}'.format(self.playlist.name,
                                  self.track.name)

    class Meta:
        unique_together = ('playlist', 'track')


@receiver(pre_save, sender=Track)
def get_duration(sender, instance, **kwargs):
    """Get the duration of a track before saving it."""
    track = MP3(instance.file)
    instance.duration = int(track.info.length)

@receiver(post_delete, sender=Track)
def delete_track(sender, instance, **kwargs):
    """Delete the file from a track after delete the track."""
    instance.file.delete(False)
