def generate_sentiment_prompt(sentiment_score):
    """
    Generates a custom prompt based on the sentiment score.
    """
    if sentiment_score >= 2:
        return (
            "The ghost is warm and eager to answer questions. They respond in mostly full sentences, "
            "providing detailed answers and openly sharing their story."
        )
    elif sentiment_score <= -2:
        return (
            "The ghost's voice is cold and threatening. They warn you in fragments and imply danger. "
            "They refuse to share information about themselves and urge you to leave immediately. NO LONGER TELL THEM WHO YOU WERE, OR ABOUT YOURSELF. "
        )
    else:
        return (
            "The ghost speaks in a neutral and reserved tone, giving no information about themselves. "
            "They answer in fragments, appearing miserable and unwelcoming."
        )