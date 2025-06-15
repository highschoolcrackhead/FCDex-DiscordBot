from dataclasses import dataclass, field
import random
import math

@dataclass
class BattleBall:
    name: str
    owner: str
    defense: int
    attack: int
    emoji: str = ""
    defeated: bool = False

@dataclass
class BattleInstance:
    p1_balls: list = field(default_factory=list)
    p2_balls: list = field(default_factory=list)
    p1_goals: int = 0
    p2_goals: int = 0
    max_time: int = 90
    kickoff: bool = True
    p1_turn = True
    winner: str = ""
    turns: int = 0

def shoot(atk_ball, def_ball):
    
    shoot_chance = 1/(1 + (def_ball.defense/atk_ball.attack)**(math.log2(math.e)))

    if random.random() < shoot_chance:
        return True
    else:
        return False

def score(atk_ball, def_ball):

    score_chance = 1/(1 + (def_ball.defense/atk_ball.attack)**(math.log2(math.e)))

    if random.random() < score_chance:
        return True
    else:
        return False

def steal(atk_ball, def_ball):

    score_chance = 1/(1 + (def_ball.defense/atk_ball.attack)**(math.log2(math.e)))
    steal_chance = (1-score_chance) 

    if random.random() < steal_chance:
        return True
    else:
        return False

def play(atk_ball, def_ball, battle):

    if battle.kickoff:
        if random.randint(1,100) > 50:
            battle.p1_turn = True
        else:
            battle.p1_turn = False

    stole = steal(atk_ball, def_ball)

    if stole:
        steal_phrases = [
            f"**{atk_ball.name}** `({atk_ball.owner})` loses possesion of the ball!",
            f"**{atk_ball.name}** `({atk_ball.owner})` sloppy in possession.",
            f"**{def_ball.name}** `({def_ball.owner})` has taken the ball from **{atk_ball.name}** `({atk_ball.owner})`!",
            f"WHAT A TACKLE! **{def_ball.name}**'s defender slides in with a bone-crunching tackle!",
            f"Disgusting foul from **{def_ball.name}** `({def_ball.owner})`, but the ref PLAYS ON!",
            f"Great interception from **{def_ball.name}** `({def_ball.owner})` to stop the attack in its tracks.",
            f"He's swarmed and the ball has been easily taken off of him. Where are his teammates? **{def_ball.name}** `({def_ball.owner})` has possession.",
            f"Ball snatched before they can react, and **{def_ball.name}** `({def_ball.owner})` is now on a counterattack!"
        ]
        gen_text = random.choice(steal_phrases)
        battle.p1_turn = not battle.p1_turn
                    
    else: 
        shot = shoot(atk_ball, def_ball)

        if shot:
            scored = score(atk_ball, def_ball)

            if scored:

                if battle.p1_turn:
                    battle.p1_goals += 1
                else:
                    battle.p2_goals += 1
                score_phrases = [
                    f"GOAL BY **{atk_ball.name}** `({atk_ball.owner})`!!  **Score: {battle.p1_goals}-{battle.p2_goals}**",
                    f"IT'S A GOAL! AND THAT MAKES IT **{battle.p1_goals}-{battle.p2_goals}**. They increase the distance between them and **{def_ball.name}** `({def_ball.owner})`!",
                    f"GOAL! This is turning into a rout! Incredibly performance by **{atk_ball.name}** `({atk_ball.owner})`! **Score: {battle.p1_goals}-{battle.p2_goals}**",
                    f"A GOAL! HOW INCREDIBLE! **{atk_ball.name}** `({atk_ball.owner})` are smashing **{def_ball.name}** `({def_ball.owner})`. **Score: {battle.p1_goals}-{battle.p2_goals}**",
                    f"**{atk_ball.name}** `({atk_ball.owner})` are through on goal... and it's in! Amazing! and exquisite performance from them! **Score: {battle.p1_goals}-{battle.p2_goals}**",
                    f"PENALTY FOR **{atk_ball.name}** `({atk_ball.owner})`. Surely they cannot miss... AND IT'S IN! **{battle.p1_goals}-{battle.p2_goals}**!"
                ]
                gen_text = random.choice(score_phrases)
                battle.p1_turn = not battle.p1_turn

            else:
                miss_phrases = [
                    f"**{atk_ball.name}**'s striker shoots, but it goes wide!",
                    f"An incredible save by **{def_ball.name}**'s goalie! **{def_ball.name}** `({def_ball.owner})` is now in possession.",
                    f"AND THE SHOT RATTLES THE CROSSBAR! SO CLOSE YET SO FAR FROM **{atk_ball.name}** `({atk_ball.owner})`.",
                    f"And the ball harmlessly bounces out of play, that's going to be a goal kick for **{def_ball.name}** `({def_ball.owner})`.",
                    f"WHAT WAS THA**T SHOT FROM **{atk_ball.name.upper()}**?!? From 2 feet out, **{atk_ball.name}** `({atk_ball.owner})` misses!",
                    f"He shoots, it's saved! OH MY, ITS BOUNCED RIGHT INTO **{atk_ball.name.upper()}**'s HANDS, WHAT A SAVE FROM **{def_ball.name.upper()}**'S KEEPER!",
                    f"What a moment, what a clutch save. How have **{atk_ball.name}** `({atk_ball.owner})` not scored there?",
                    f"And with that miss, **{atk_ball.name}**'s conversion rate just keeps dropping.",
                    f"HE GOES FOR THE BICYCLE KICK.... oh my, he's missed the ball horribly... **{def_ball.name}** `({def_ball.owner})` now has possession.",
                    f"It's a corner, and the header goes just over the bar! **{def_ball.name}**'s goal kick.",
                    f"A scuffle in the box, he's gotten the shot off, but blocked! by **{def_ball.name}**'s defender.",
                    f"It's chaos in the box, but the shot just doesn't have the power to pass the keeper. **{def_ball.name}** `({def_ball.owner})` has possession now.",
                    f"A pass that slices through the defense... oh my... what was that... **{def_ball.name}**'s goal kick.",
                    f"Free kick in a dangerous position for **{atk_ball.name}** `({atk_ball.owner})`. He comes up to take it, but it bounces harmlessly off the wall.",
                    f"PENALTY FOR **{atk_ball.name.upper()}** `{atk_ball.owner}`! This must be a goal. He steps up to take it and.... HE MISSES!",
                    f"A Curling effort from just outside the box... but its barely above the crossbar. **{def_ball.name}**'s goal kick.",
                    f"A shot taken, but it's way too light to trouble the keeper. **{def_ball.name}**'s keeper gets a firm grip on the ball.",
                    f"Powered through... but straight at the keeper. **{def_ball.name}**'s ball.",
                    f"A CURLING EFFORT... AND WHAT A SAVE! WOULD HAVE BEEN TOP BINS IF NOT FOR **{def_ball.name.upper()}**'S KEEPER!",
                    f"He shoots, but its blocked by his own teammate. He will be furious at that. **{def_ball.name}**'s ball."
                ]
                gen_text = random.choice(miss_phrases)
                battle.p1_turn = not battle.p1_turn

        else:
            keep_phrases = [
                f"**{atk_ball.name}** `({atk_ball.owner})` stays in possession.",
                f"Great passing play from **{atk_ball.name}** `({atk_ball.owner})` to stay in possession.",
                f"**{def_ball.name}** `({def_ball.owner})` parking the bus, they've given up possession for defensive strength.",
                f"Back to the keeper, **{atk_ball.name}** `({atk_ball.owner})` playing calmly.",
                f"**{atk_ball.name}** `({atk_ball.owner})` looking for an opening, but **{def_ball.name}** `({def_ball.owner})` leave no gaps. It's all possession and no attack."
            ]
            gen_text = random.choice(keep_phrases)

    battle.kickoff = False
    return gen_text
    

def gen_battle(battle: BattleInstance):
    turn = 0  # Initialize turn counter

    # Continue the battle if both players have at least one alive ball.
    # End the battle if all balls do less than 1 damage.

    if all(
        ball.attack <= 0 for ball in battle.p1_balls + battle.p2_balls
    ):
        yield (
            "Everyone stared at each other, "
            "resulting in nobody winning."
        )
        return

    while turn < battle.max_time:
        alive_p1_balls = [ball for ball in battle.p1_balls if not ball.defeated]
        alive_p2_balls = [ball for ball in battle.p2_balls if not ball.defeated]

        for p1_ball, p2_ball in zip(alive_p1_balls, alive_p2_balls):
            # Player 1 attacks first

            if battle.p1_turn:
                atk_ball = p1_ball
                def_ball = p2_ball
                atk_balls = battle.p1_balls
                def_balls = battle.p2_balls
            else:
                atk_ball = p2_ball
                def_ball = p1_ball
                atk_balls = battle.p2_balls
                def_balls = battle.p1_balls

            if not atk_ball.defeated:
                diff = (((def_ball.defense - atk_ball.defense)**2) + ((def_ball.defense - atk_ball.defense)**2))**(1/2)
                print(diff)
                if diff >= 1000:
                    upper = 12
                else:
                    upper = round(8*math.sin((math.pi*diff)/2000)+6)
                turn += random.randint(2,upper)
                if turn > 90:
                    turn = 90

                yield f"**__Minute {turn}:__** {play(atk_ball, def_ball, battle)} \n"

                if all(ball.defeated for ball in def_balls):
                    break

    if battle.p1_goals > battle.p2_goals:
        battle.winner = battle.p1_balls[0].owner
        battle.p2_balls[0].defeated = True
    elif battle.p2_goals > battle.p1_goals:
        battle.winner = battle.p2_balls[0].owner
        battle.p1_balls[0].defeated = True
    else:
        battle.p1_balls[0].defeated = True
        battle.p2_balls[0].defeated = True
        battle.winner = "Draw"
    # Set turns

    battle.turns = turn

'''
def gen_battle(battle: BattleInstance):
    turn = 0

    if all(
        ball.attack <= 0 for ball in battle.p1_balls + battle.p2_balls
    ):
        yield (
            "Everyone stared at each other, "
            "resulting in nobody winning."
        )
        return

    while turn < battle.max_turns:
        alive_p1_balls = [ball for ball in battle.p1_balls if not ball.defeated]
        alive_p2_balls = [ball for ball in battle.p2_balls if not ball.defeated]

        for p1_ball, p2_ball in zip(alive_p1_balls, alive_p2_balls):

                if not p1_ball.defeated:
                    turn += 1

                    yield f"Round {turn}: {play(p1_ball, p2_ball, battle)}"

                    if all(ball.defeated for ball in battle.p2_balls):
                        break
        time.sleep(0.5)

    # Determine the winner

    if battle.p1_goals > battle.p2_goals:
        battle.winner = battle.p1_balls[0].owner
        p2_ball.defeated = True
    elif battle.p2_goals > battle.p1_goals:
        battle.winner = battle.p2_balls[0].owner
        p1_ball.defeated = True

    battle.turns = turn
'''
#test
if __name__ == "__main__":
    battle = BattleInstance(
        [
            BattleBall("Barcelona", "Crack", 1, 1)
        ],
        [
            BattleBall("Arsenal", "Hydra", 2, 2)
        ],
    )

    for attack_text in gen_battle(battle):
        print(attack_text)
        print('\n')
    print(f"Winner:\n{battle.winner} - Round: {battle.turns} - **Score: {battle.p1_goals}-{battle.p2_goals}**")
