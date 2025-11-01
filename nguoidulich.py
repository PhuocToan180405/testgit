import random
import math
import matplotlib.pyplot as plt
import numpy as np

class GeneticTSP:
    def __init__(self, cities, population_size=100, generations=500, 
                 mutation_rate=0.02, elite_size=20):
        """
        Khởi tạo giải thuật di truyền cho TSP
        - cities: danh sách tọa độ thành phố [[x1,y1], [x2,y2], ...]
        - population_size: kích thước quần thể
        - generations: số thế hệ
        - mutation_rate: tỷ lệ đột biến
        - elite_size: số cá thể tốt nhất được giữ lại
        """
        self.cities = cities
        self.num_cities = len(cities)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
    def calculate_distance(self, city1, city2):
        """Tính khoảng cách Euclidean giữa hai thành phố"""
        return math.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)
    
    def calculate_route_distance(self, route):
        """Tính tổng khoảng cách của một lộ trình"""
        distance = 0
        for i in range(len(route)):
            distance += self.calculate_distance(
                self.cities[route[i]], 
                self.cities[route[(i+1) % len(route)]]
            )
        return distance
    
    def fitness(self, route):
        """Hàm fitness - ngược với khoảng cách (càng ngắn càng tốt)"""
        return 1 / self.calculate_route_distance(route)
    
    def create_population(self):
        """Tạo quần thể ngẫu nhiên ban đầu"""
        population = []
        for _ in range(self.population_size):
            route = list(range(self.num_cities))
            random.shuffle(route)
            population.append(route)
        return population
    
    def selection(self, population):
        """Lựa chọn cá thể cha mẹ bằng phương pháp Tournament Selection"""
        tournament_size = 5
        tournament1 = random.sample(population, min(tournament_size, len(population)))
        tournament2 = random.sample(population, min(tournament_size, len(population)))
        
        parent1 = min(tournament1, key=lambda x: self.calculate_route_distance(x))
        parent2 = min(tournament2, key=lambda x: self.calculate_route_distance(x))
        return parent1, parent2
    
    def crossover(self, parent1, parent2):
        """Lai ghép hai cha mẹ bằng Order Crossover (OX)"""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        
        child = [-1] * size
        child[start:end] = parent1[start:end]
        
        pointer = end
        for city in parent2[end:] + parent2[:end]:
            if city not in child:
                if pointer >= size:
                    pointer = 0
                child[pointer] = city
                pointer += 1
        
        return child
    
    def mutate(self, route):
        """Đột biến bằng cách đảo ngược một đoạn ngẫu nhiên"""
        if random.random() < self.mutation_rate:
            start, end = sorted(random.sample(range(len(route)), 2))
            route[start:end+1] = reversed(route[start:end+1])
        return route
    
    def evolve(self):
        """Chạy giải thuật di truyền"""
        population = self.create_population()
        
        for generation in range(self.generations):
            # Tính fitness cho tất cả cá thể
            fitness_scores = [self.fitness(route) for route in population]
            
            # Ghi lại thông tin quần thể
            distances = [self.calculate_route_distance(route) for route in population]
            self.best_fitness_history.append(min(distances))
            self.avg_fitness_history.append(np.mean(distances))
            
            # Chọn lọc - giữ lại elite_size cá thể tốt nhất
            ranked = sorted(zip(population, distances), key=lambda x: x[1])
            elite_population = [route for route, _ in ranked[:self.elite_size]]
            
            # Tạo thế hệ mới
            new_population = elite_population.copy()
            while len(new_population) < self.population_size:
                parent1, parent2 = self.selection(population)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            population = new_population
            
            if (generation + 1) % 100 == 0:
                best_distance = min(distances)
                print(f"Thế hệ {generation + 1}: Khoảng cách tốt nhất = {best_distance:.2f}")
        
        # Tìm lộ trình tốt nhất cuối cùng
        best_route = min(population, key=self.calculate_route_distance)
        best_distance = self.calculate_route_distance(best_route)
        
        return best_route, best_distance
    
    def visualize(self, route, title="Lộ trình TSP"):
        """Hiển thị lộ trình tốt nhất"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Vẽ lộ trình
        ax = axes[0]
        route_cities = [self.cities[i] for i in route] + [self.cities[route[0]]]
        route_array = np.array(route_cities)
        ax.plot(route_array[:, 0], route_array[:, 1], 'b-', linewidth=1.5, alpha=0.6)
        ax.scatter(route_array[:, 0], route_array[:, 1], c='red', s=200, zorder=5, edgecolors='darkred', linewidth=2)
        
        for i, (x, y) in enumerate(self.cities):
            ax.annotate(f'{i}', (x, y), fontsize=10, ha='center', va='center', 
                       fontweight='bold', color='white', zorder=6)
        
        ax.set_title(f'{title}\nKhoảng cách: {self.calculate_route_distance(route):.2f}', fontsize=12)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        
        # Vẽ biểu đồ sự hội tụ
        ax = axes[1]
        ax.plot(self.best_fitness_history, label='Khoảng cách tốt nhất', linewidth=2)
        ax.plot(self.avg_fitness_history, label='Khoảng cách trung bình', 
                linewidth=2, alpha=0.7)
        ax.set_xlabel('Thế hệ')
        ax.set_ylabel('Khoảng cách')
        ax.set_title('Sự hội tụ của giải thuật')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


# Ví dụ sử dụng
if __name__ == "__main__":
    # Tạo 20 thành phố ngẫu nhiên
    random.seed(42)
    num_cities = 20
    cities = [[random.uniform(0, 100), random.uniform(0, 100)] 
              for _ in range(num_cities)]
    
    # Khởi tạo và chạy giải thuật
    ga = GeneticTSP(cities, population_size=100, generations=500, 
                    mutation_rate=0.02, elite_size=20)
    
    print("Đang chạy giải thuật di truyền...")
    best_route, best_distance = ga.evolve()
    
    print(f"\nKết quả tốt nhất:")
    print(f"Lộ trình: {best_route}")
    print(f"Khoảng cách tổng cộng: {best_distance:.2f}")
    
    # Hiển thị kết quả
    ga.visualize(best_route)