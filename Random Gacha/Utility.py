import random

class MarbleBagRandom:
    def __init__(self, elements, seed=None):
        assert len(elements) > 0, "elements list must not be empty."
        self.bag = []  # start with an empty bag
        self.o_bag = elements  # original bag
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def draw(self):
        if not self.bag:
            self.bag = self.o_bag.copy()  # refill the bag from the original
            random.shuffle(self.bag)  # shuffle the bag randomly
        return self.bag.pop()  # draw an element


class Predetermination:
    def __init__(self, max_attempts, seed=None) -> None:
        assert max_attempts > 0, "max attempts must be a positive integer."
        self.attempts = 0
        self.success_at = random.randint(1, max_attempts)
        self.max_attempts = max_attempts
        if seed is not None:
            random.seed(seed)

    def attempt(self):
        self.attempts += 1
        if self.attempts >= self.success_at:
            self.attempts = 0
            return True
        return False


class FixedRateProb:
    def __init__(self, probability, fixed_success_rate, seed=None) -> None:
        assert 0 <= probability <= 100, "probability must be between 0 and 100."
        assert fixed_success_rate > 0, "fixed success rate must be a positive integer."
        self.attempt_count = 0
        self.fixed_success_rate = fixed_success_rate
        self.base_probability = probability
        if seed is not None:
            random.seed(seed)

    def attempt(self):
        self.attempt_count += 1
        if self.attempt_count >= self.fixed_success_rate:
            self.attempt_count = 0
            return True
        
        roll = int(random.uniform(0, 100))
        if roll < self.base_probability:
            self.attempt_count = 0
            return True
        else:
            return False


class ProgressiveProb:
    def __init__(self, success_rate, increment, seed=None) -> None:
        assert 0 <= success_rate <= 100, "success rate must be between 0 and 100."
        assert isinstance(increment, (int, float)), "increment must be a number." # this allow any value
        self.base_success_rate = success_rate
        self.current_success_rate = self.base_success_rate
        self.increment = increment
        if seed is not None:
            random.seed(seed)

    def reset_probability(self):
        self.current_success_rate = self.base_success_rate

    def attempt(self):
        p = random.uniform(0, 100)
        if p < self.current_success_rate:
            self.reset_probability()
            return True
        else:
            self.current_success_rate += self.increment
            return False
