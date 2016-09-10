from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Greeting,User,Movie,Rating,Cluster
from sklearn.cluster import KMeans
from scipy.sparse import dok_matrix, csr_matrix
import numpy as np

# Create your views here.
def index(request):
    #return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

def cluster(request):
    all_user_id = map(lambda x : x.userid, User.objects.all())
    all_movie_id = set(map(lambda x:x.movieid, Movie.objects.all()))
    ratings_mat = dok_matrix((max(all_user_id), max(all_movie_id)+1), dtype=np.float32)
    for uid in range(1,max(all_user_id)):
        users_reviews = Rating.objects.filter(userid=uid)
        for review in users_reviews:
            ratings_mat[uid,review.movieid] = review.rating
    kmeans = KMeans(n_clusters=19)
    clustering = kmeans.fit(ratings_mat.tocsr())

    Cluster.objects.all().delete()
    new_clusters = {i: Cluster.objects.create(name=i) for i in range(19)}
    for i,cluster_label in enumerate(clustering.labels_):
            new_clusters[cluster_label].users.add(User.objects.get(userid=all_user_id[i]))
    return HttpResponse("Generated clusters")

def getid(request):
    if request.method == 'POST' :
        userid = request.POST['userid']
        request.session['id'] = userid
        return redirect('/recommend/')
    else:
        return render(request, 'getid.html')