from django.shortcuts import render,get_object_or_404

from .models import Post,Comment
from taggit.models import Tag

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger 
from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank
from .forms import EmailPostForm,CommentForm,SearchForm

from django.db.models import Count
#Trigram
from django.contrib.postgres.search import TrigramSimilarity
# Create your views here.
def post_list(request,tag_slug=None):
    object_list=Post.published.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])
    paginator=Paginator(object_list,2) #2 Posts in each page
    page = request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts=paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts= paginator.page(paginator.num_pages)
    

    context={'page':page,'posts':posts,'tag':tag}
    return render(request,'blog/post/list.html',context)

def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post,
                        status='published',
                        publish__year=year,
                        publish__month=month,
                        publish__day=day
                        )
   
    #List of active comments for this post
    comments=post.comments.filter(active=True)
    new_comment = None
    
    if request.method=='POST':
        #A comment was posted
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            #Create comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            #Asign the current post to the comment
            new_comment.post=post
            #Save the comment to the database
            new_comment.save()
    else:
        comment_form=CommentForm()
    
    #List of similar posts
    post_tag_ids = post.tags.values_list('id',flat=True)
    similar_posts= Post.published.filter(tags__in=post_tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    context={'post':post,'comments':comments,'new_comment':new_comment,'comment_form':comment_form,'similar_posts':similar_posts}

    return  render(request,'blog/post/detail.html',context)

def post_share(request,post_id):
    #retrieve post by id
    post= get_object_or_404(Post,id=post_id,status='published')
    if request.method== "POST":
        #Form was submitted
        form =EmailPostForm(request.POST)
        if form.is_valid():
            #Form fields passed validation
            cd=form.cleaned_data
    else:
        form= EmailPostForm()
    return render(request,'blog/post/share.html',{'post':post,'form':form})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            
            search_query = SearchQuery(query)
            #Trigram similarty for title search
            #results = Post.published.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')
            
            #Full-Text seach To seach body and title
            search_vector = SearchVector('title', 'body')
            
            results = Post.published.annotate(search=search_vector,rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')
           
            #Rank and weight search for body and title
            #search_vector = SearchVector('title',weight='A') + SearchVector('body',weight='B')
            #results = Post.published.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
    return render(request,'blog/post/search.html',{'form':form,'query':query,'results':results})
