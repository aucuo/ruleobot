import {User} from "../entities/User";

export interface IUserRepository {
    save(user: User): Promise<void>; // Сохранить пользователя
    findById(userId: number): Promise<User | null>; // Найти пользователя по ID
    delete(userId: number): Promise<void>; // Удалить пользователя
}
