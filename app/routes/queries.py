from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)


@queries_bp.route("/list_tables")
def list_tables():
    """List all tables in the database."""

    # >>>> TODO 1: Write a query to list all the tables in the database. <<<<

    query = """SHOW TABLES;"""

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)


@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    """Search for movies by name."""
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """SELECT name, rating, production, budget FROM MotionPicture WHERE name Like %s;"""
    
    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    """Search for movies liked by a specific user."""
    user_email = request.form["user_email"]

    # >>>> TODO 3: Find the movies that have been liked by a specific user’s email. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """SELECT M.name, M.rating, M.production, M.budget FROM Likes L, MotionPicture M WHERE L.uemail Like %s AND L.mpid = M.id;"""

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    """Search for movies by country using the Location table."""
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """SELECT DISTINCT M.name FROM MotionPicture M, Location L WHERE M.id = L.mpid AND L.country Like %s;"""

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    """Search for directors and the series they directed by zip code."""
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed TV series shot in a specific zip code. <<<<
    #              List the director name and TV series name only without duplicates.

    query = """WITH Directors AS (SELECT * FROM Role WHERE role_name = 'Director') 
            SELECT P.name, M.name FROM Directors D, People P, MotionPicture M, Location L  
            WHERE D.mpid = M.id AND D.pid = P.id AND L.mpid = M.id AND L.zip = %s;"""

    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    """Search for award records where the award count is greater than `k`."""
    k = int(request.form["k"])

    # >>>> TODO 6: Find the people who have received more than “k” awards for a single motion picture in the same year. <<<<
    #              List the person `name`, `motion picture name`, `award year` and `award count`.

    query = """SELECT P.name, M.name, A.award_year, COUNT(*) AS award_count FROM People P, MotionPicture M, Award A 
                WHERE P.id = A.pid AND M.id = A.mpid
                GROUP BY P.id, M.id, A.award_year
                HAVING COUNT(*) > %s;"""

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():
    """
    Find the youngest and oldest actors based on the difference 
    between the award year and their date of birth.
    """

    # >>>> TODO 7: Find the youngest and oldest actors to win at least one award. <<<<
    #              List the actor names and their age (at the time they received the award). 
    #              The age should be computed from the person’s date of birth to the award winning year only. 
    #              In case of a tie, list all of them.

    query = """WITH Actors AS (
                SELECT 
                    P.id,
                    P.name,
                    P.dob,
                    A.award_year,
                    (A.award_year - YEAR(P.dob)) AS age
                FROM People P
                JOIN Role R ON P.id = R.pid
                JOIN Award A ON P.id = A.pid AND R.mpid = A.mpid
                WHERE R.role_name = 'Actor'
            ),
            Age AS (
                SELECT 
                    MIN(age) AS youngest_age,
                    MAX(age) AS oldest_age
                FROM Actors
            )
            SELECT AT.name, AT.age
            FROM Actors AT
            JOIN Age AG 
            ON AT.age = AG.youngest_age OR AT.age = AG.oldest_age
            ORDER BY AT.age;
            """

    with Database() as db:
        actors = db.execute(query)
    
    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    """
    Search for American producers based on a minimum box office collection and maximum budget.
    """
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: Find the American [USA] Producers who had a box office collection of more than or equal to “X” with a budget less than or equal to “Y”. <<<< 
    #              List the producer `name`, `movie name`, `box office collection` and `budget`.

    query = """With Producers AS (
                SELECT P.name, R.mpid 
                FROM People P, Role R
                WHERE P.id = R.pid AND R.role_name = 'Producer' AND P.nationality = 'USA')
                SELECT P.name, MP.name, M.boxoffice_collection, MP.budget
                FROM Producers P, MotionPicture MP, Movie M
                WHERE P.mpid = MP.id AND MP.id = M.mpid AND M.boxoffice_collection >= %s AND MP.budget <= %s;"""

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    """
    Search for people who have multiple roles in movies with a rating above a given threshold.
    """
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the people who have played multiple roles in a motion picture where the rating is more than “X”. <<<<
    #              List the person’s `name`, `motion picture name` and `count of number of roles` for that particular motion picture.

    query = """WITH MPs AS (
                SELECT id, name
                FROM MotionPicture
                WHERE rating > %s)
                SELECT P.name, MP.name, COUNT(*) AS role_count
                FROM People P, Role R, MPs MP
                WHERE P.id = R.pid AND R.mpid = MP.id
                GROUP BY P.id, MP.id
                HAVING COUNT(*) > 1;"""

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    """Display the top 2 thriller movies in Boston based on rating."""

    # >>>> TODO 10: Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. <<<<
    #               This means that the movie cannot have any other shooting location. 
    #               List the `movie names` and their `ratings`.

    query = """SELECT M.name, M.rating FROM MotionPicture M, Genre G WHERE G.genre_name = 'Thriller' AND M.id = G.mpid AND id IN (SELECT mpid FROM Location WHERE city = 'Boston') ORDER BY rating DESC LIMIT 2;"""

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)



@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    """
    Search for movies that have received more than a specified number of likes,
    where the liking users are below a certain age.
    """
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” likes by users of age less than “Y”. <<<<
    #               List the movie names and the number of likes by those age-group users.

    query = """WITH UserAge AS (
                SELECT email, age
                FROM Users
                WHERE age < %s)
                SELECT M.name, COUNT(*) AS likes_count
                FROM Likes L, UserAge U, MotionPicture M
                WHERE L.uemail = U.email AND L.mpid = M.id
                GROUP BY M.id
                HAVING COUNT(*) > %s;"""

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    """
    List actors who have appeared in movies produced by both Marvel and Warner Bros.
    """

    # >>>> TODO 12: Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the `actor names` and the corresponding `motion picture names`.

    query = """WITH MarvelActors AS (
                    SELECT DISTINCT P.id, P.name AS actor_name, MP.name AS movie_name
                    FROM People P
                    JOIN Role R ON P.id = R.pid
                    JOIN MotionPicture MP ON R.mpid = MP.id
                    WHERE MP.production = 'Marvel'
                ),
                WarnerActors AS (
                    SELECT DISTINCT P.id, P.name AS actor_name, MP.name AS movie_name
                    FROM People P
                    JOIN Role R ON P.id = R.pid
                    JOIN MotionPicture MP ON R.mpid = MP.id
                    WHERE MP.production = 'Warner Bros'
                )
                SELECT M.actor_name, M.movie_name 
                FROM MarvelActors M
                WHERE M.id IN (SELECT W.id FROM WarnerActors W)
                UNION
                SELECT W.actor_name, W.movie_name 
                FROM WarnerActors W
                WHERE W.id IN (SELECT M.id FROM MarvelActors M);
                """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    """
    Display movies whose rating is higher than the average rating of comedy movies.
    """

    # >>>> TODO 13: Find the motion pictures that have a higher rating than the average rating of all comedy (genre) motion pictures. <<<<
    #               Show the names and ratings in descending order of ratings.

    query = """SELECT name, rating 
                FROM MotionPicture 
                WHERE rating > (SELECT AVG(M.rating) 
                                FROM MotionPicture M, Genre G 
                                WHERE G.genre_name = 'Comedy' AND M.id = G.mpid) 
                ORDER BY rating DESC;"""

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


@queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
def top_5_movies_people_roles():
    """
    Display the top 5 movies that involve the most people and roles.
    """

    # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
    #               Show the `movie name`, `people count` and `role count` for the movies.

    query = """SELECT MP.name AS movie_name, COUNT(DISTINCT R.pid) AS people_count, COUNT(R.role_name) AS role_count
                FROM Movie M, MotionPicture MP, Role R
                WHERE M.mpid = MP.id AND M.mpid = R.mpid
                GROUP BY MP.name
                ORDER BY people_count DESC, role_count DESC
                LIMIT 5;
                """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    """
    Find pairs of actors who share the same birthday.
    """

    # >>>> TODO 15: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """WITH Actors AS (
                SELECT DISTINCT id, name, dob
                FROM People P, Role R
                WHERE P.id = R.pid AND R.role_name = 'Actor')
                SELECT A1.name, A2.name, A1.dob
                FROM Actors A1, Actors A2
                WHERE A1.dob = A2.dob AND A1.id < A2.id;"""

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)