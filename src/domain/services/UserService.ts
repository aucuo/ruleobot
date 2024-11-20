import { User } from "../entities/User";
import { IUserRepository } from "../repositories/IUserRepository";

export class UserService {
    constructor(private userRepository: IUserRepository) {}

    // Сохранение пользователя
    async saveUser(user: User): Promise<void> {
        await this.userRepository.save(user);
    }

    // Обновление времени активности пользователя
    async updateLastActive(userId: number): Promise<void> {
        const user = await this.userRepository.findById(userId);
        if (!user) {
            throw new Error(`User with ID ${userId} not found`);
        }
        user.updateLastActive();
        await this.userRepository.save(user);
    }

    // Удаление пользователя
    async deleteUser(userId: number): Promise<void> {
        await this.userRepository.delete(userId);
    }
}
